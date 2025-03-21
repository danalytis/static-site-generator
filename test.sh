#This ensures that the src directory is included in the Python path, allowing imports
export PYTHONPATH=$(pwd)/src
#Run our tests
python3 -m unittest discover -s src/test
