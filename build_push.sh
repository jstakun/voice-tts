podman build -f ./Dockerfile -t quay.io/jstakun/voice-tts:slim
podman push --authfile ~/jstakun-aiassistant-auth.json quay.io/jstakun/voice-tts:slim
