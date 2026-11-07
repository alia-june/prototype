cmake_minimum_required(VERSION 3.20)
project(gfx_form_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(GFX_ENABLE_HIP "Enable HIP backend scaffolding" OFF)

add_library(gfx_form
    src/runtime/reference.cpp
    src/runtime/recursion.cpp
    src/workloads/json0/lexical.cpp
    src/workloads/json0/parser.cpp
)
target_include_directories(gfx_form PUBLIC include)

if (MSVC)
  target_compile_options(gfx_form PRIVATE /W4 /permissive-)
else()
  target_compile_options(gfx_form PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(gfx_smoke examples/smoke.cpp)
target_link_libraries(gfx_smoke PRIVATE gfx_form)

include(CTest)
if(BUILD_TESTING)
  add_executable(test_atomic tests/test_atomic.cpp)
  target_link_libraries(test_atomic PRIVATE gfx_form)
  add_test(NAME atomic COMMAND test_atomic)

  add_executable(test_reference tests/test_reference.cpp)
  target_link_libraries(test_reference PRIVATE gfx_form)
  add_test(NAME reference COMMAND test_reference)

  add_executable(test_recursion tests/test_recursion.cpp)
  target_link_libraries(test_recursion PRIVATE gfx_form)
  add_test(NAME recursion COMMAND test_recursion)

  add_executable(test_frame_cast tests/test_frame_cast.cpp)
  target_link_libraries(test_frame_cast PRIVATE gfx_form)
  add_test(NAME frame_cast COMMAND test_frame_cast)

  add_executable(test_json0 tests/test_json0.cpp)
  target_link_libraries(test_json0 PRIVATE gfx_form)
  add_test(NAME json0 COMMAND test_json0)
  add_executable(test_json0_parser tests/test_json0_parser.cpp)
  target_link_libraries(test_json0_parser PRIVATE gfx_form)
  add_test(NAME json0_parser COMMAND test_json0_parser)

  add_executable(test_triplane tests/test_triplane.cpp)
  target_link_libraries(test_triplane PRIVATE gfx_form)
  add_test(NAME triplane COMMAND test_triplane)

  add_executable(test_runtime tests/test_runtime.cpp)
  target_link_libraries(test_runtime PRIVATE gfx_form)
  add_test(NAME runtime COMMAND test_runtime)

  add_executable(test_composition tests/test_composition.cpp)
  target_link_libraries(test_composition PRIVATE gfx_form)
  add_test(NAME composition COMMAND test_composition)

  add_executable(test_frame_mapping tests/test_frame_mapping.cpp)
  target_link_libraries(test_frame_mapping PRIVATE gfx_form)
  add_test(NAME frame_mapping COMMAND test_frame_mapping)

  add_executable(test_recursion_monitor tests/test_recursion_monitor.cpp)
  target_link_libraries(test_recursion_monitor PRIVATE gfx_form)
  add_test(NAME recursion_monitor COMMAND test_recursion_monitor)
endif()
