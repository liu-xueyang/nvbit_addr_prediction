NVBIT_PATH=../../core
INCLUDES=-I$(NVBIT_PATH)

all: $(NVBIT_PATH)/libnvbit.a
	nvcc -ccbin=$(CXX) $(INCLUDES) -O3 -arch=sm_61 vectoradd.cu -o vectoradd

clean:
	rm -f vectoradd
