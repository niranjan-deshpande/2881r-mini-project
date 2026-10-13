#!/bin/bash
# Runs ON the pod, unattended. Sets up, downloads weights to the network volume, runs session1, then deletes the pod
# whether the job succeeded or failed (outputs stay on the network volume at /workspace/out).
#   nohup bash /workspace/code/gpu/run_pod.sh > /workspace/run_pod.log 2>&1 &
set -u
W=/workspace
STAGES=${STAGES:-check,pairs,dirs,rollouts,lenses,manifest}
terminate() {
  echo "[$(date +%T)] exit; deleting pod ${RUNPOD_POD_ID:-?}"; sync
  runpodctl pod delete "$RUNPOD_POD_ID" || runpodctl remove pod "$RUNPOD_POD_ID"
}
trap terminate EXIT
set -x
cd $W/code
python3 -m venv --system-site-packages $W/venv
$W/venv/bin/pip install -q "transformers==5.19.0" accelerate "flash-linear-attention==0.5.2" huggingface_hub numpy pyarrow
$W/venv/bin/python -c "import torch, fla, transformers; print(torch.__version__, torch.cuda.get_device_name(0), transformers.__version__)" || exit 1
[ -f $W/models/Qwen3.8-27B/config.json ] || $W/venv/bin/hf download Qwen/Qwen3.8-27B --local-dir $W/models/Qwen3.8-27B || exit 1
if [ ! -f $W/models/jpp/qwen3.6-27b/lens.pt ]; then
  $W/venv/bin/hf download koayon/jpp-lenses qwen3.6-27b/lens.pt --local-dir $W/models/jpp || echo "J++ lens download failed; skipping borrowed J++"
fi
export JPP_LENS=$W/models/jpp/qwen3.6-27b/lens.pt
timeout 5h $W/venv/bin/python gpu/session1.py --model $W/models/Qwen3.8-27B --data $W/data --out $W/out --stages "$STAGES"
echo "[$(date +%T)] session1 exit code $?"
