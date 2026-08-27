# Experiment records

This directory stores small, versioned records needed to understand and reproduce experiments.
Keep run configurations, metrics, summaries, notes, and selected plots here.

Do not commit high-frequency or large artifacts such as checkpoints, videos, TensorBoard/W&B data,
raw trajectories, recordings, or datasets. The local `.gitignore` excludes these artifacts.

## Create a record on the experiment computer

Copy the template and name the directory with a date and short experiment name:

```bash
cp -r experiment_records/template experiment_records/2026-08-27_example
```

Fill in `run.yaml`, `summary.json`, `metrics.csv`, and `notes.md`, then commit and push to Gitee:

```bash
git add experiment_records/2026-08-27_example
git commit -m "Record 2026-08-27 example experiment"
git push origin main
```

On a computer cloned from Gitee, `origin` is the Gitee repository.

## Receive the record on the development computer

The development computer names the Gitee remote `gitee` and GitHub `origin`:

```bash
git switch main
git pull --ff-only gitee main
git push origin main
```

This pulls the experiment record from Gitee and mirrors the same commit to GitHub.

## Large artifacts

Transfer required final checkpoints or raw data separately, for example with `scp`, `rsync`, a NAS,
or dedicated artifact storage. Record the artifact filename, checksum, and storage location in
`notes.md` so the run remains traceable.

