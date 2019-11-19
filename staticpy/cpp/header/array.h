#include <vector>
#include <stdarg.h>
#ifdef PYBIND
#include <pybind11/pybind11.h>
namespace py = pybind11;
#endif

template <typename T, long ndim>
class Array {
public:
    const T *data;
    const long *shape;
    const long *strides;
    const long dim = ndim;
    const long itemsize;
    #ifdef PYBIND
    Array(py::buffer_info& bi) : 
        data((T*)bi.ptr), shape(bi.shape.data()), strides(bi.strides.data()), itemsize(bi.itemsize) {
    }
    #endif
    Array(T* data, std::vector<long>& shape, std::vector<long>& strides, long itemsize) : 
        data(data), shape(shape.data()), strides(strides.data()), itemsize(itemsize) {
    }

    inline T& operator[](long index) {
        return data[index];
    }

    template<typename Integer>
    inline T& getData(Integer index0, ...) {
        // transform numpy-like index to C-like index
        va_list args;
        va_start(args, index0);
        long indices[ndim];
        indices[0] = (long)index0;
        for (unsigned short i = 1; i < ndim; i++) {
            indices[i] = (long)va_arg(args, Integer);
        }
        va_end(args);
        long offset = 0;
        for (unsigned short i = 0; i < ndim; i++) {
            offset += strides[i] * indices[i];
        }
        return *(T *)((char *)data + offset);
    }

};