#include <vector>
#include <stdarg.h>
#ifdef PYBIND
#include <pybind11/pybind11.h>
namespace py = pybind11;
#endif

template <typename T, long ndim, bool wrap=true>
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

    template<typename Integer>
    inline T& getData(Integer index0, ...) {
        // transform numpy-like index to C-like index
        va_list args;
        va_start(args, index0);
        long offset = wrap_index(static_cast<long>(index0)) * strides[0];
        for (unsigned short i = 1; i < ndim; i++) {
            offset += wrap_index(static_cast<long>(va_arg(args, Integer))) * strides[i];
        }
        va_end(args);
        return *(T *)((char *)data + offset);
    }
protected:
    virtual inline long wrap_index(long index, int dim) const {
        const long shape = this->shape[dim];
        if (-shape <= index && index < 0) {
            index += shape;
        } else if (index >= shape || index < -shape) {
            throw std::exception("invalid index");
        }
        return index;
    }

};


template <typename T, long ndim>
class Array<T, ndim, false>: public Array<T, ndim, true> {
public:
    #ifdef PYBIND
    Array(py::buffer_info& bi) : Array<T, ndim, true>(bi) {
    }
    #endif
    Array(T* data, std::vector<long>& shape, std::vector<long>& strides, long itemsize) : 
        Array<T, ndim, true>(data, shape, strides, itemsize) {
    }

protected:
    inline long wrap_index(long index, int dim) const override {
        return index;
    }
};
