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
    client = None
    container = None

    try:
        # 初始化 Docker 客户端
        client = docker.from_env()

        # 创建并启动容器（不立即等待）
        container = client.containers.run(
            image="python:3.11-alpine",  # 轻量级镜像
            command=["python", "-c", code],
            detach=True,  # 后台运行
            mem_limit="128m",  # 限制内存 128MB
            cpu_quota=50000,  # 限制 CPU (50%)
            network_disabled=True,  # 禁止网络访问（安全）
            remove=False,  # 先不删除，等获取日志后再删
        )

        # 等待容器执行完成（带超时）
        result = container.wait(timeout=timeout)

        # 获取输出
        logs = container.logs(stdout=True, stderr=True).decode('utf-8')

        # 检查退出码
        exit_code = result.get('StatusCode', -1)

        # 删除容器
        try:
            container.remove(force=True)
        except:
            pass

        if exit_code == 0:
            return True, logs
        else:
            return False, logs

    except docker.errors.ImageNotFound:
        return False, (
            "Docker 镜像未找到\n"
            "请先拉取镜像: docker pull python:3.11-alpine"
        )

    except docker.errors.APIError as e:
        return False, f"Docker API 错误: {str(e)}\n请确保 Docker 服务已启动"

    except Exception as e:
        # 如果出错，尝试清理容器
        if container:
            try:
                container.remove(force=True)
            except:
                pass

        # 检查是否是超时错误
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            return False, f"执行超时 (>{timeout}秒)"

        return False, f"执行错误: {str(e)}"
