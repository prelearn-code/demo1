"""多模型管理器"""

from typing import Dict, List
from dataclasses import dataclass

from langchain_ollama import ChatOllama


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    model_id: str
    temperature: float
    max_tokens: int
    description: str


class ModelManager:
    """多模型管理器"""

    def __init__(self):
        self.models = {
            "qwen-7b": ModelConfig(
                name="Qwen2.5-Coder 7B",
                model_id="qwen2.5-coder:7b",
                temperature=0.0,
                max_tokens=2048,
                description="轻量级，速度快"
            ),
            "qwen-14b": ModelConfig(
                name="Qwen2.5-Coder 14B",
                model_id="qwen2.5-coder:14b",
                temperature=0.0,
                max_tokens=2048,
                description="性能更强，需要更多资源"
            ),
            "qwen-32b": ModelConfig(
                name="Qwen2.5-Coder 32B",
                model_id="qwen2.5-coder:32b",
                temperature=0.0,
                max_tokens=2048,
                description="最强性能，资源消耗最大"
            ),
            "deepseek": ModelConfig(
                name="DeepSeek-Coder 6.7B",
                model_id="deepseek-coder:6.7b",
                temperature=0.0,
                max_tokens=2048,
                description="备选模型"
            ),
            "codellama": ModelConfig(
                name="CodeLlama 7B",
                model_id="codellama:7b",
                temperature=0.0,
                max_tokens=2048,
                description="Meta 开源代码模型"
            )
        }

    def get_llm(self, model_key: str, temperature: float = None):
        """
        获取指定模型的 LLM 实例

        Args:
            model_key: 模型键名
            temperature: 温度参数，如果为 None 则使用配置中的默认值

        Returns:
            ChatOllama 实例
        """
        if model_key not in self.models:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(self.models.keys())}")

        config = self.models[model_key]

        return ChatOllama(
            model=config.model_id,
            temperature=temperature if temperature is not None else config.temperature
        )

    def list_models(self) -> List[Dict]:
        """
        列出所有可用模型

        Returns:
            模型信息列表
        """
        return [
            {
                "key": key,
                "name": config.name,
                "model_id": config.model_id,
                "description": config.description
            }
            for key, config in self.models.items()
        ]

    def compare_report(self, results: Dict) -> str:
        """
        生成对比报告

        Args:
            results: 模型结果字典，格式：
                {
                    "qwen-7b": {
                        "success_rate": 0.52,
                        "avg_iterations": 2.3,
                        "correction_lift": 0.17
                    },
                    ...
                }

        Returns:
            格式化的对比报告
        """
        report = ["=" * 60]
        report.append("模型对比结果")
        report.append("=" * 60)

        for model_key, metrics in results.items():
            if model_key not in self.models:
                continue

            model_name = self.models[model_key].name
            report.append(f"\n{model_name} ({model_key}):")
            report.append(f"  成功率: {metrics.get('success_rate', 0):.2%}")
            report.append(f"  平均迭代: {metrics.get('avg_iterations', 0):.1f}")
            report.append(f"  自纠错提升: +{metrics.get('correction_lift', 0):.2%}")

            if 'total_tasks' in metrics:
                report.append(f"  任务总数: {metrics['total_tasks']}")
            if 'avg_time' in metrics:
                report.append(f"  平均耗时: {metrics['avg_time']:.1f}秒")

        report.append("\n" + "=" * 60)

        # 找出最佳模型
        if results:
            best_model = max(results.items(), key=lambda x: x[1].get('success_rate', 0))
            report.append(f"最佳模型: {self.models[best_model[0]].name}")
            report.append("=" * 60)

        return "\n".join(report)

    def get_model_info(self, model_key: str) -> Dict:
        """
        获取模型详细信息

        Args:
            model_key: 模型键名

        Returns:
            模型配置字典
        """
        if model_key not in self.models:
            raise ValueError(f"Unknown model: {model_key}")

        config = self.models[model_key]
        return {
            "name": config.name,
            "model_id": config.model_id,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "description": config.description
        }
