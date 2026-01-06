"""
代码执行沙箱 - Docker 容器隔离
使用 Docker 容器安全执行 Python 代码
"""
import docker
from typing import Tuple


def execute_code(code: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    在 Docker 容器中安全执行 Python 代码

    Args:
        code: 要执行的 Python 代码
        timeout: 超时时间(秒)

    Returns:
        (是否成功, 输出或错误信息)
    """
    try:
        # 初始化 Docker 客户端
        client = docker.from_env()

        # 在隔离容器中执行代码
        result = client.containers.run(
            image="python:3.11-alpine",  # 轻量级镜像
            command=["python", "-c", code],
            remove=True,  # 执行后自动删除容器
            mem_limit="128m",  # 限制内存 128MB
            cpu_quota=50000,  # 限制 CPU (50%)
            network_disabled=True,  # 禁止网络访问（安全）
            read_only=True,  # 只读文件系统（防止篡改）
            timeout=timeout,
            stdout=True,
            stderr=True
        )

        # 返回成功和输出
        return True, result.decode('utf-8')

    except docker.errors.ContainerError as e:
        # 容器执行错误（代码报错）
        return False, e.stderr.decode('utf-8')

    except docker.errors.ImageNotFound:
        return False, (
            "Docker 镜像未找到\n"
            "请先拉取镜像: docker pull python:3.11-alpine"
        )

    except docker.errors.APIError as e:
        return False, f"Docker API 错误: {str(e)}\n请确保 Docker 服务已启动"

    except Exception as e:
        return False, f"执行错误: {str(e)}"
