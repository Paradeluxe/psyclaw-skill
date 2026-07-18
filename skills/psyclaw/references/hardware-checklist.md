# Hardware / Environment Pre-Flight Checks

## Why

心理学实验最大的 confound 之一是被试端硬件不一致：
- 屏幕刷新率不对 → 视觉呈现 timing 全毁
- 没戴耳机 → 音频实验无效
- 键盘延迟不一致 → RT 数据不可比

## Solution: `checklist_injector.py`

自动扫描 spec 中的组件类型，注入对应的 pre-experiment 检查 routine。

```
spec 里有…                 → 自动注入的 check routine
─────────────────────────────────────────────────────────
audio 组件                 → headphone_check（播放 800Hz 纯音 + Y/N 确认）
image / video 组件         → screen_check（显示十字 + Y/N 确认）
text 组件（始终有）         → screen_check（默认注入）
keyboard 且 store 非空     → latency_check（5 次按键 RT 校准）
```

## Injection point

Check routines 插入在 `instructions` 之后、第一个 trial loop 之前。
在 PsychoPy Flow 中位于 trial loop 外面，每个被试只跑一次。

## Usage

```bash
python scripts/checklist_injector.py specs/experiment.yaml --output specs/experiment_checked.yaml
```

输出 spec 可继续走正常流水线（flow_gen_transform → emit → validate）。

## Stimulus assets

`headphone_check` 需要 `assets/check_tone.wav`（800Hz, 0.5s, fade in/out）。
`checklist_injector.py` 自动往 spec 的 `stimuli` block 添加 `check_tone` 条目，
主流水线的 `stimulus_generator.py` 会在 stage 7 生成它。

## Verified

| Experiment | Checks injected | PsychoPy loadFromXML |
|------------|----------------|---------------------|
| KFS (audio + visual) | headphone_check, screen_check | 0 warnings (1171 params) |
| art.pics (visual) | screen_check | pending |

## Future checks (to implement)

- refresh_rate_check — pyglet vsync 检测, < 60Hz 警告（需要 CodeComponent）
- volume_calibration — 放参考音, 滑块校准至"刚好听到"
- browser_fingerprint_check — 在线实验用 (User-Agent, viewport, WebGL)
- demographics_check — 被试号/年龄/性别采集（始终注入）
