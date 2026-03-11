import os
from openai import OpenAI
from pathlib import Path

os.environ["DASHSCOPE_API_KEY"] = "sk-1a7eef79673b4ab3af60ecb03e69be81"





client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

file_object = client.files.create(file=Path(r"E:\ProjLegacy\DeepPsych\experiment.txt"), purpose="file-extract")
# client.files.create(
#     file=Path(r"E:\ProjLegacy\DeepPsych\JSON schemas\StimList\exp_json.json"),
#     purpose="fine-tune"
# )
# print(file_object)
file = client.files.retrieve(file_id="file-fe-4bb1734eba2a47f7b4c209d4")

print(file.model_dump_json())


exit()

# completion = client.chat.completions.create(
#     # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
#     model="qwen3.5-flash-2026-02-23",
#     messages=[
#         {"role": "system", "content": [
#             {"type": "text", "text": '请根据exp_json.json和experiment.txt，只关注到exp_json.json里的所有变量（即"$"开头的变量），生成符合Variables.json这个schema的格式的输出.json。请不要给予任何解释。'}
#             {"type": "file", "file_id": file_object.id}
#         ]},
#     ]
# )
# print(completion.model_dump_json())