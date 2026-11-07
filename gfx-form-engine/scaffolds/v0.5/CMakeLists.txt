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
  foreach(test_name IN ITEMS
      atomic
      reference
      recursion
      frame_cast
      json0
      json0_parser
      triplane
      runtime
      composition
      frame_mapping
      recursion_monitor
      backing_route
      frame_graph
      elr_planes
      json_relations
      recovery_route)
    add_executable(test_${test_name} tests/test_${test_name}.cpp)
    target_link_libraries(test_${test_name} PRIVATE gfx_form)
    add_test(NAME ${test_name} COMMAND test_${test_name})
  endforeach()
endif()
