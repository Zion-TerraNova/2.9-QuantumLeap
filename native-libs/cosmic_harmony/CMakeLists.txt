cmake_minimum_required(VERSION 3.15)
project(ZionCosmicHarmony VERSION 2.9.0 LANGUAGES C CXX)

# Set OpenSSL Root for Windows
if(WIN32)
    set(OPENSSL_ROOT_DIR "C:/Program Files/OpenSSL-Win64")
endif()

# Find required packages
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)

# Source files
set(COSMIC_HARMONY_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/zion-cosmic-harmony.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cosmic_harmony_c_wrapper.cpp
)

# Compile Blake3 from source
message(STATUS "Compiling Blake3 from source")
set(BLAKE3_C_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../external/blake3/c)

if(EXISTS ${BLAKE3_C_DIR}/blake3.c)
    # Add Blake3 C sources (choose ISA files based on architecture)
    set(BLAKE3_SOURCES
        ${BLAKE3_C_DIR}/blake3.c
        ${BLAKE3_C_DIR}/blake3_dispatch.c
        ${BLAKE3_C_DIR}/blake3_portable.c
    )

    if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm64|aarch64)$")
        message(STATUS "Blake3: ARM detected, enabling NEON")
        list(APPEND BLAKE3_SOURCES ${BLAKE3_C_DIR}/blake3_neon.c)
    else()
        message(STATUS "Blake3: x86_64 detected, enabling SSE/AVX")
        list(APPEND BLAKE3_SOURCES
            ${BLAKE3_C_DIR}/blake3_sse2.c
            ${BLAKE3_C_DIR}/blake3_sse41.c
            ${BLAKE3_C_DIR}/blake3_avx2.c
            ${CMAKE_CURRENT_SOURCE_DIR}/blake3_avx512_stub.c
        )

        # Set SIMD-specific compile flags (x86 only)
        if(MSVC)
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_sse2.c PROPERTIES COMPILE_FLAGS "/arch:SSE2")
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_sse41.c PROPERTIES COMPILE_FLAGS "/arch:AVX") # MSVC doesn't have specific SSE4.1 flag, AVX implies it
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_avx2.c PROPERTIES COMPILE_FLAGS "/arch:AVX2")
        else()
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_sse2.c PROPERTIES COMPILE_FLAGS "-msse2")
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_sse41.c PROPERTIES COMPILE_FLAGS "-msse4.1")
            set_source_files_properties(${BLAKE3_C_DIR}/blake3_avx2.c PROPERTIES COMPILE_FLAGS "-mavx2")
        endif()
    endif()
    
    list(APPEND COSMIC_HARMONY_SOURCES ${BLAKE3_SOURCES})
    include_directories(${BLAKE3_C_DIR})
else()
    message(FATAL_ERROR "Blake3 source not found at ${BLAKE3_C_DIR}")
endif()

# Create shared library
add_library(cosmic_harmony SHARED ${COSMIC_HARMONY_SOURCES})

# Include directories
target_include_directories(cosmic_harmony PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/include
    ${OPENSSL_INCLUDE_DIR}
)

# Link libraries
target_link_libraries(cosmic_harmony
    OpenSSL::SSL
    OpenSSL::Crypto
    Threads::Threads
)

# Compiler optimizations
if(MSVC)
    target_compile_options(cosmic_harmony PRIVATE
        /O2
        /fp:fast
        /Oi
        /Ot
    )
else()
    target_compile_options(cosmic_harmony PRIVATE
        -O3
        -ffast-math
        -funroll-loops
        -finline-functions
    )
endif()

# Platform-specific settings
if(WIN32)
    set_target_properties(cosmic_harmony PROPERTIES
        OUTPUT_NAME "cosmic_harmony_zion"
        SUFFIX ".dll"
        VERSION ${PROJECT_VERSION}
        SOVERSION 2
    )
elseif(APPLE)
    set_target_properties(cosmic_harmony PROPERTIES
        OUTPUT_NAME "cosmic_harmony_zion"
        SUFFIX ".dylib"
        INSTALL_RPATH "@loader_path"
        VERSION ${PROJECT_VERSION}
        SOVERSION 2
    )
else()
    set_target_properties(cosmic_harmony PROPERTIES
        OUTPUT_NAME "cosmic_harmony_zion"
        SUFFIX ".so"
        INSTALL_RPATH "$ORIGIN"
        VERSION ${PROJECT_VERSION}
        SOVERSION 2
    )
endif()

# Install
install(TARGETS cosmic_harmony
    LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
    RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
    ARCHIVE DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining
)

# Copy to project root for easy Python access
if(WIN32)
    add_custom_command(TARGET cosmic_harmony POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:cosmic_harmony>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/libcosmic_harmony_zion.dll
        COMMENT "Copying cosmic_harmony library to zion/mining/"
    )
elseif(APPLE)
    add_custom_command(TARGET cosmic_harmony POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:cosmic_harmony>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/libcosmic_harmony_zion.dylib
        COMMENT "Copying cosmic_harmony library to zion/mining/ (macOS dylib)"
    )
    add_custom_command(TARGET cosmic_harmony POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:cosmic_harmony>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining/libcosmic_harmony_zion.dylib
        COMMENT "Copying cosmic_harmony library to ai/mining/ (macOS dylib)"
    )
else()
    add_custom_command(TARGET cosmic_harmony POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:cosmic_harmony>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../zion/mining/libcosmic_harmony_zion.so.${PROJECT_VERSION}
        COMMENT "Copying cosmic_harmony library to zion/mining/"
    )
    add_custom_command(TARGET cosmic_harmony POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
            $<TARGET_FILE:cosmic_harmony>
            ${CMAKE_CURRENT_SOURCE_DIR}/../../ai/mining/libcosmic_harmony_zion.so.${PROJECT_VERSION}
        COMMENT "Copying cosmic_harmony library to ai/mining/"
    )
endif()

message(STATUS "Cosmic Harmony library configured")
message(STATUS "  Sources: ${COSMIC_HARMONY_SOURCES}")
message(STATUS "  Target: 100k-500k H/s (5-25x speedup)")
