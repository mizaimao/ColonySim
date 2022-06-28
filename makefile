# system python interpreter. used only to create virtual environment
PY = python3
VENV = .venv
BIN=$(VENV)/bin
TEMP=temp


.PHONY: venv
venv: clean standard_venv build_cv2_ft post_venv

.PHONY: standard_venv
standard_venv:
	$(PY) -m venv $(VENV)
	$(BIN)/pip install --upgrade -r requirements.txt
	touch $(VENV)

.PHONY: build_cv2_ft
build_cv2_ft:
	# export CMAKE_ARGS="-DWITH_FREETYPE=ON -DBUILD_opencv_freetype=ON" ENABLE_CONTRIB=1
	# mkdir $(TEMP); cd $(TEMP); git clone --recursive https://github.com/opencv/opencv-python.git; cd opencv-python; pip wheel . --verbose; python -m pip install opencv_contrib_python*.whl
	# rm -rf $(TEMP)
	$(BIN)/pip install --upgrade opencv-python

.PHONY: post_venv
post_venv:
	$(BIN)/pip install -e .
	
.PHONY: test
test: $(VENV)
	$(BIN)/pytest

.PHONY: lint
lint: $(VENV)
	pylint

.PHONY: clean
clean:
	deactivate
	rm -rf $(VENV)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete