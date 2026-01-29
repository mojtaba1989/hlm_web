#include <opencv2/opencv.hpp>
#include <atomic>
#include <mutex>
#include <thread>
#include <chrono>
#include <fstream>
#include <csignal>
#include <zmq.hpp>
#include <string>


bool TCP_ENABLED = false;
cv::Mat latestFrame;
std::mutex frameMutex;
std::atomic<bool> running(true);
zmq::context_t zmq_ctx(1);
zmq::socket_t zmq_pub(zmq_ctx, ZMQ_PUB);

struct  __attribute__((packed)) Packet {
    uint32_t frame_id = 0;
    uint64_t unix_time;
} pkt;


void signalHandler(int signum) {
    std::cout << "\nStopping recording..." << std::endl;
    running = false;
}

void initZMQ() {
    if (!TCP_ENABLED) return;
    zmq_pub.bind("tcp://127.0.0.1:5556");
    std::this_thread::sleep_for(std::chrono::seconds(1));
    std::cout << "ZMQ initialized" << std::endl;
}

void captureThread(const std::string &cam = "/dev/video0") {
    cv::VideoCapture cap(cam);

    if (!cap.isOpened()) {
        std::cerr << "ERROR: Cannot open camera: " << cam << std::endl;
        std::exit(1);   // or std::exit(1)
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 720);
    cap.set(cv::CAP_PROP_FPS, 30);

    cv::Mat frame;

    while (running) {
        cap >> frame;
        if (frame.empty()) continue;

        std::lock_guard<std::mutex> lock(frameMutex);
        latestFrame = frame.clone();
    }

    cap.release();
}

void writerThread(const std::string &filename, double fps) {
    using clock = std::chrono::steady_clock;
    auto period = std::chrono::duration_cast<std::chrono::steady_clock::duration>(
                  std::chrono::duration<double>(1.0 / fps));
    
    std::string csv_filename = filename + ".csv";
    std::ofstream csv(csv_filename);
    csv << "time_nsec,frame_id\n";

    cv::Mat lastFrame;
    bool writerOpened = false;
    cv::VideoWriter writer;

    auto start = clock::now();
    auto nextTick = start;
    struct Packet pkt_;

    while (running) {
        nextTick += period;

        {
            std::lock_guard<std::mutex> lock(frameMutex);
            if (!latestFrame.empty()) {
                lastFrame = latestFrame.clone();
            }
        }

        if (!lastFrame.empty()) {
            if (!writerOpened) {
                writer.open(filename,
                            cv::VideoWriter::fourcc('M','J','P','G'),
                            fps,
                            lastFrame.size());
                writerOpened = true;
            }

            writer.write(lastFrame);

            auto now = std::chrono::system_clock::now();
            auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
            pkt_.unix_time = static_cast<uint64_t>(ns);
            csv << pkt_.unix_time << "," << pkt_.frame_id << "\n";
            pkt_.frame_id++;
            if (TCP_ENABLED){
                zmq::message_t msg(sizeof(Packet));
                memcpy(msg.data(), &pkt_, sizeof(Packet));
                zmq_pub.send(msg, zmq::send_flags::none);
            }
            
        }

        std::this_thread::sleep_until(nextTick);
    }

    running = false;
    writer.release();
    csv.close();
}


int main(int argc, char** argv) {
    std::signal(SIGINT, signalHandler);

    initZMQ();
    std::cout << "Recording started:"<< argv[1] << std::endl;
    std::string camera = (argc > 2) ? argv[2] : "/dev/video0";
    std::thread capT(captureThread, camera);
    std::thread wrT(writerThread, argv[1], 30.0);

    capT.join();
    wrT.join();

    std::cout << "Recording finished cleanly." << std::endl;
    return 0;
}
