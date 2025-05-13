#!/bin/bash
# Script to wait for RTSP streams to be ready

# Default values
HOST="localhost"
PORT=8554
TIMEOUT=60
INTERVAL=2
STREAMS=("/standard" "/ptz" "/audio" "/multi-object" "/license-plate")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --timeout=*)
      TIMEOUT="${1#*=}"
      shift
      ;;
    --interval=*)
      INTERVAL="${1#*=}"
      shift
      ;;
    --streams=*)
      IFS=',' read -ra STREAMS <<< "${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Waiting for RTSP streams to be ready..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Timeout: $TIMEOUT seconds"
echo "Check interval: $INTERVAL seconds"
echo "Streams to check: ${STREAMS[*]}"

# Function to check if a stream is ready
check_stream() {
  local stream=$1
  local url="rtsp://$HOST:$PORT$stream"
  
  # Use ffprobe to check if the stream is available
  if ffprobe -v quiet -rtsp_transport tcp -i "$url" -show_entries stream=codec_type -of csv=p=0 &>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Wait for all streams to be ready
start_time=$(date +%s)
all_ready=false

while ! $all_ready; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))
  
  if [ $elapsed -ge $TIMEOUT ]; then
    echo "Timeout reached. Not all streams are ready."
    exit 1
  fi
  
  all_ready=true
  
  for stream in "${STREAMS[@]}"; do
    if check_stream "$stream"; then
      echo "Stream $stream is ready"
    else
      echo "Stream $stream is not ready yet"
      all_ready=false
    fi
  done
  
  if ! $all_ready; then
    echo "Waiting $INTERVAL seconds before checking again..."
    sleep $INTERVAL
  fi
done

echo "All streams are ready!"
exit 0
