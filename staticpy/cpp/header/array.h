#pragma once
#include <vector>
#include <stdarg.h>
#include <stdexcept>
#ifdef PYBIND
#include <pybind11/pybind11.h>
namespace py = pybind11;
#endif

template <typename T, long ndim>
class Array {
public:
    const T *data;
    const std::vector<long>& shape;
    const std::vector<long>& strides;
    const long dim = ndim;
    const long itemsize;
    #ifdef PYBIND
    Array(py::buffer_info& bi) : 
        data((T*)bi.ptr), shape(bi.shape), strides(bi.strides), itemsize(bi.itemsize) {
    }
    #endif
    Array(const T* data, const std::vector<long>& shape, const std::vector<long>& strides, long itemsize) : 
        data(data), shape(shape), strides(strides), itemsize(itemsize) {
    }

};
