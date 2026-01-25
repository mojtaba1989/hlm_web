cmake_minimum_required(VERSION 3.16)
project(hlm_web)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)
if(NOT OpenCV_FOUND)
    message(FATAL_ERROR "OpenCV not found")
endif()

# Find ZeroMQ
find_package(PkgConfig REQUIRED)
pkg_check_modules(ZMQ REQUIRED libzmq)
if(NOT ZMQ_FOUND)
    message(FATAL_ERROR "ZeroMQ not found")
endif()

# Add executable
add_executable(rec rec.cpp)

# Include directories
target_include_directories(rec PRIVATE ${OpenCV_INCLUDE_DIRS} ${ZMQ_INCLUDE_DIRS})

# Link libraries
target_link_libraries(rec PRIVATE ${OpenCV_LIBS} ${ZMQ_LIBRARIES})
