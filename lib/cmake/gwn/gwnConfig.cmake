INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_GWN gwn)

FIND_PATH(
    GWN_INCLUDE_DIRS
    NAMES gwn/api.h
    HINTS $ENV{GWN_DIR}/include
        ${PC_GWN_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GWN_LIBRARIES
    NAMES gnuradio-gwn
    HINTS $ENV{GWN_DIR}/lib
        ${PC_GWN_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GWN DEFAULT_MSG GWN_LIBRARIES GWN_INCLUDE_DIRS)
MARK_AS_ADVANCED(GWN_LIBRARIES GWN_INCLUDE_DIRS)

