# ZION RandomX Native Mining Module
# CMake build configuration for RandomX algorithm
# Performance target: 2,000-10,000 H/s (CPU optimized)

cmake_minimum_required(VERSION 3.15)
project(zion-randomx VERSION 2.9.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Find RandomX library first
find_package(RandomX QUIET)

if(NOT RandomX_FOUND)
    message(STATUS "RandomX library not found, building from source...")
    
    # Check if external/randomx exists (relative to build_zion parent)
    # Path to RandomX source (cloned separately)
set(RANDOMX_SOURCE_DIR "${CMAKE_SOURCE_DIR}/../../external/randomx")
    if(EXISTS "${RANDOMX_SOURCE_DIR}/CMakeLists.txt")
        message(STATUS "  Found RandomX source: ${RANDOMX_SOURCE_DIR}")
        
        # Set RandomX build options
        set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build static RandomX" FORCE)
        set(ARCH "native" CACHE STRING "CPU architecture" FORCE)
        
        # Add RandomX subdirectory
        add_subdirectory(${RANDOMX_SOURCE_DIR}
                         ${CMAKE_BINARY_DIR}/randomx_lib
                         EXCLUDE_FROM_ALL)
        
        # Set variables for our wrapper
        set(RANDOMX_LIBRARY randomx)
        set(RANDOMX_INCLUDE_DIR ${RANDOMX_SOURCE_DIR}/src)
        set(RANDOMX_FOUND TRUE)
    else()
        message(WARNING "RandomX source not found at ${RANDOMX_SOURCE_DIR}")
        message(STATUS "  Run: git clone https://github.com/tevador/RandomX.git external/randomx")
        return()
    endif()
else()
    message(STATUS "Found system RandomX library: ${RANDOMX_LIBRARY}")
    set(RANDOMX_INCLUDE_DIR ${RANDOMX_INCLUDE_DIRS})
endif()

# Source files for our wrapper
set(ZION_RANDOMX_SOURCES
    zion-randomx.cpp
    randomx_c_wrapper.cpp
)

# Create ZION RandomX shared library
add_library(randomx_zion SHARED ${ZION_RANDOMX_SOURCES})

# Set library properties
set_target_properties(randomx_zion PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "randomx_zion"
    PREFIX "lib"
)

# Include directories
target_include_directories(randomx_zion
    PRIVATE
        ${RANDOMX_INCLUDE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link RandomX library
if(WIN32)
    target_link_libraries(randomx_zion
        PRIVATE
            ${RANDOMX_LIBRARY}
    )
else()
    target_link_libraries(randomx_zion
        PRIVATE
            ${RANDOMX_LIBRARY}
            pthread
    )
endif()

# Compiler optimizations (matching Cosmic Harmony)
if(MSVC)
    target_compile_options(randomx_zion PRIVATE
        /O2
        /Ot
        /Oi
        /fp:fast
    )
else()
    target_compile_options(randomx_zion PRIVATE
        -O3
        -march=native
        -mtune=native
        -ffast-math
        -fno-strict-aliasing
    )
endif()

# Install to zion/mining
install(TARGETS randomx_zion
    LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/../../ai/mining
    RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/../../ai/mining
    ARCHIVE DESTINATION ${CMAKE_SOURCE_DIR}/../../ai/mining
)

# Copy to project directories immediately after build (for Python runtime + packaging)
if(WIN32)
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../ai/mining/librandomx_zion.dll
        COMMENT "Copying RandomX library to ai/mining/"
    )
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../zion/mining/librandomx_zion.dll
        COMMENT "Copying RandomX library to zion/mining/"
    )
elseif(APPLE)
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../ai/mining/librandomx_zion.dylib
        COMMENT "Copying RandomX library to ai/mining/ (macOS dylib)"
    )
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../zion/mining/librandomx_zion.dylib
        COMMENT "Copying RandomX library to zion/mining/ (macOS dylib)"
    )
else()
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../ai/mining/librandomx_zion.so.${PROJECT_VERSION}
        COMMENT "Copying RandomX library to ai/mining/"
    )
    add_custom_command(TARGET randomx_zion POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:randomx_zion>
            ${CMAKE_SOURCE_DIR}/../../zion/mining/librandomx_zion.so.${PROJECT_VERSION}
        COMMENT "Copying RandomX library to zion/mining/"
    )
endif()

# Install versioned library (Linux/macOS only)
if(UNIX AND NOT APPLE)
    install(CODE "
        execute_process(
            COMMAND ${CMAKE_COMMAND} -E create_symlink
                librandomx_zion.so.${PROJECT_VERSION}
                ${CMAKE_SOURCE_DIR}/../../ai/mining/librandomx_zion.so
        )
    ")
endif()

message(STATUS "ZION RandomX module configured")
message(STATUS "  RandomX library: ${RANDOMX_LIBRARY}")
message(STATUS "  Include dir: ${RANDOMX_INCLUDE_DIR}")
message(STATUS "  Target performance: 2,000-10,000 H/s")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
