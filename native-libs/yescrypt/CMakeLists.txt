cmake_minimum_required(VERSION 3.15)
project(ZionYescrypt VERSION 2.9.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags (match Yescrypt's native Makefile)
if(MSVC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /O2 /Ot /Oi /arch:AVX2 /openmp /DSKIP_MEMZERO")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2 /Ot /Oi /arch:AVX2 /openmp")
else()
    # AppleClang doesn't support -fopenmp directly; OpenMP is configured per-target below.
    if(APPLE)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -O3 -march=native -fomit-frame-pointer -DSKIP_MEMZERO")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3 -march=native -fomit-frame-pointer")
    else()
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -O3 -march=native -fomit-frame-pointer -fopenmp -DSKIP_MEMZERO")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3 -march=native -fomit-frame-pointer -fopenmp")
    endif()
endif()

set(ZION_LIBOMP_ROOT "" CACHE PATH "Path to Homebrew libomp (macOS only)")

# OpenMP: on macOS use Homebrew libomp; elsewhere use standard -fopenmp / OpenMP package.
if(APPLE)
    if(ZION_LIBOMP_ROOT STREQUAL "")
        set(ZION_LIBOMP_ROOT "/opt/homebrew/opt/libomp")
    endif()
    if(EXISTS "${ZION_LIBOMP_ROOT}/include/omp.h")
        message(STATUS "Using libomp from: ${ZION_LIBOMP_ROOT}")
        set(ZION_ENABLE_OPENMP TRUE)
    else()
        message(WARNING "libomp not found at ${ZION_LIBOMP_ROOT}. Install via: brew install libomp")
        set(ZION_ENABLE_OPENMP FALSE)
    endif()
elseif(NOT MSVC)
    find_package(OpenMP QUIET)
    if(OpenMP_C_FOUND)
        message(STATUS "OpenMP found: enabling")
        set(ZION_ENABLE_OPENMP TRUE)
    else()
        message(STATUS "OpenMP not found: continuing without explicit OpenMP")
        set(ZION_ENABLE_OPENMP FALSE)
    endif()
endif()

# Yescrypt source directory
set(YESCRYPT_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../external/yescrypt")

# Yescrypt core sources
set(YESCRYPT_SOURCES
    ${YESCRYPT_SRC_DIR}/yescrypt-opt.c
    ${YESCRYPT_SRC_DIR}/yescrypt-common.c
    ${YESCRYPT_SRC_DIR}/sha256.c
    ${YESCRYPT_SRC_DIR}/insecure_memzero.c
)

# Include directories
include_directories(${YESCRYPT_SRC_DIR})

# Build static Yescrypt library
add_library(yescrypt_static STATIC ${YESCRYPT_SOURCES})
set_target_properties(yescrypt_static PROPERTIES 
    OUTPUT_NAME yescrypt
    POSITION_INDEPENDENT_CODE ON
)

# ZION wrapper sources
set(ZION_WRAPPER_SOURCES
    zion-yescrypt.cpp
    yescrypt_c_wrapper.cpp
)

# Build shared library with ZION wrapper
add_library(yescrypt_zion SHARED ${ZION_WRAPPER_SOURCES})

if(WIN32)
    target_link_libraries(yescrypt_zion PRIVATE yescrypt_static)
else()
    target_link_libraries(yescrypt_zion PRIVATE yescrypt_static pthread)
    if(APPLE AND ZION_ENABLE_OPENMP)
        target_compile_options(yescrypt_static PRIVATE -Xpreprocessor -fopenmp)
        target_compile_options(yescrypt_zion PRIVATE -Xpreprocessor -fopenmp)
        target_include_directories(yescrypt_static PRIVATE "${ZION_LIBOMP_ROOT}/include")
        target_include_directories(yescrypt_zion PRIVATE "${ZION_LIBOMP_ROOT}/include")
        target_link_libraries(yescrypt_zion PRIVATE "${ZION_LIBOMP_ROOT}/lib/libomp.dylib")
    elseif(OpenMP_C_FOUND)
        target_link_libraries(yescrypt_zion PRIVATE OpenMP::OpenMP_C OpenMP::OpenMP_CXX)
    endif()
endif()

set_target_properties(yescrypt_zion PROPERTIES 
    VERSION ${PROJECT_VERSION}
    SOVERSION 2
    OUTPUT_NAME "yescrypt_zion"
)

# Install library to Python directory
install(TARGETS yescrypt_zion
    LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
    RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
    ARCHIVE DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
)

# Copy to Python directory immediately after build
if(WIN32)
    add_custom_command(TARGET yescrypt_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:yescrypt_zion>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining/libyescrypt_zion.dll
        COMMENT "Copying Yescrypt library to ai/mining/"
    )
elseif(APPLE)
    add_custom_command(TARGET yescrypt_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:yescrypt_zion>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining/libyescrypt_zion.dylib
        COMMENT "Copying Yescrypt library to ai/mining/ (macOS dylib)"
    )
    add_custom_command(TARGET yescrypt_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:yescrypt_zion>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/libyescrypt_zion.dylib
        COMMENT "Copying Yescrypt library to zion/mining/ (macOS dylib)"
    )
else()
    add_custom_command(TARGET yescrypt_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:yescrypt_zion>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining/libyescrypt_zion.so.${PROJECT_VERSION}
        COMMENT "Copying Yescrypt library to ai/mining/"
    )
    add_custom_command(TARGET yescrypt_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:yescrypt_zion>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/libyescrypt_zion.so.${PROJECT_VERSION}
        COMMENT "Copying Yescrypt library to zion/mining/"
    )
endif()

# Optional: Build tests
option(BUILD_TESTS "Build test executables" ON)
if(BUILD_TESTS)
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/test_yescrypt_basic.cpp")
        add_executable(test_yescrypt_basic test_yescrypt_basic.cpp)
        target_link_libraries(test_yescrypt_basic yescrypt_zion)
    endif()
    
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/test_yescrypt_performance.cpp")
        add_executable(test_yescrypt_performance test_yescrypt_performance.cpp)
        target_link_libraries(test_yescrypt_performance yescrypt_zion pthread)
    endif()
endif()

message(STATUS "=== ZION Yescrypt v${PROJECT_VERSION} ===")
message(STATUS "Source: ${YESCRYPT_SRC_DIR}")
message(STATUS "Target: 500-2,000 H/s native")
message(STATUS "OpenMP: Enabled for multi-threading")
message(STATUS "Optimizations: -O3 -march=native -fopenmp")
