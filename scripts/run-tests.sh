#!/bin/bash
# Script to run Arkos AI tests locally

# Default values
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false
SKIP_RTSP=false
SKIP_MEDIA_GEN=false
SKIP_LINT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --test-type=*)
      TEST_TYPE="${1#*=}"
      shift
      ;;
    --no-coverage)
      COVERAGE=false
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --skip-rtsp)
      SKIP_RTSP=true
      shift
      ;;
    --skip-media-gen)
      SKIP_MEDIA_GEN=true
      shift
      ;;
    --skip-lint)
      SKIP_LINT=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set working directory to project root
cd "$(dirname "$0")/.." || exit 1

# Print test configuration
echo "Running Arkos AI tests..."
echo "Test type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo "Verbose: $VERBOSE"
echo "Skip RTSP: $SKIP_RTSP"
echo "Skip Media Generation: $SKIP_MEDIA_GEN"
echo "Skip Linting: $SKIP_LINT"

# Set up coverage and verbosity options
COVERAGE_OPTS=""
if $COVERAGE; then
  COVERAGE_OPTS="--cov=arkos --cov-report=term --cov-report=xml"
fi

VERBOSE_OPTS=""
if $VERBOSE; then
  VERBOSE_OPTS="-v"
fi

# Run linting if not skipped
if ! $SKIP_LINT; then
  echo "Running linting..."
  
  # Run pre-commit hooks
  pre-commit run --all-files
  
  # Run pylint
  pylint arkos/ --disable=C0111,C0103,C0303,W0511,R0903,R0902,R0913,R0914 --max-line-length=100 --ignore=migrations --extension-pkg-whitelist=numpy,cv2,tensorflow
  
  # Run mypy
  mypy arkos/ --ignore-missing-imports --disallow-untyped-defs --disallow-incomplete-defs --check-untyped-defs --disallow-untyped-decorators --no-implicit-optional --warn-redundant-casts --warn-return-any --warn-unused-ignores
fi

# Generate test media if not skipped
if ! $SKIP_MEDIA_GEN; then
  echo "Generating test media..."
  python tests/fixtures/media_generator.py
fi

# Start RTSP simulator if not skipped
if ! $SKIP_RTSP; then
  echo "Starting RTSP simulator..."
  
  # Check if Docker is running
  if ! docker info &>/dev/null; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
  fi
  
  # Start RTSP simulator
  docker-compose -f tests/docker/rtsp-streams.yml up -d
  
  # Wait for RTSP streams to be ready
  chmod +x scripts/wait-for-streams.sh
  ./scripts/wait-for-streams.sh --timeout=60
  
  if [ $? -ne 0 ]; then
    echo "Error: RTSP streams are not ready. Stopping tests."
    docker-compose -f tests/docker/rtsp-streams.yml down
    exit 1
  fi
fi

# Run tests based on test type
case $TEST_TYPE in
  "unit")
    echo "Running unit tests..."
    python -m pytest tests/unit/ $VERBOSE_OPTS $COVERAGE_OPTS
    ;;
  "integration")
    echo "Running integration tests..."
    python -m pytest tests/integration/ $VERBOSE_OPTS $COVERAGE_OPTS
    ;;
  "rtsp")
    echo "Running RTSP tests..."
    python -m pytest tests/rtsp/ $VERBOSE_OPTS $COVERAGE_OPTS
    ;;
  "performance")
    echo "Running performance tests..."
    python -m pytest tests/performance/ $VERBOSE_OPTS --benchmark-json=benchmark.json
    ;;
  "e2e")
    echo "Running end-to-end tests..."
    python -m pytest tests/e2e/ $VERBOSE_OPTS $COVERAGE_OPTS
    ;;
  "all")
    echo "Running all tests..."
    python -m pytest tests/ $VERBOSE_OPTS $COVERAGE_OPTS
    ;;
  *)
    echo "Unknown test type: $TEST_TYPE"
    exit 1
    ;;
esac

# Store test result
TEST_RESULT=$?

# Stop RTSP simulator if it was started
if ! $SKIP_RTSP; then
  echo "Stopping RTSP simulator..."
  docker-compose -f tests/docker/rtsp-streams.yml down
fi

# Print test result
if [ $TEST_RESULT -eq 0 ]; then
  echo "Tests passed!"
else
  echo "Tests failed!"
fi

exit $TEST_RESULT
