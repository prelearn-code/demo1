"""
代码执行沙箱
使用 subprocess 在本地执行 Python 代码 (警告: 不安全,仅用于演示)
"""
import subprocess
import tempfile
import os
from typing import Tuple


def execute_code(code: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    执行 Python 代码

    Args:
        code: 要执行的 Python 代码
        timeout: 超时时间(秒)

    Returns:
        (是否成功, 输出或错误信息)
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(code)
        temp_file = f.name

    try:
        # 执行代码
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        # 检查执行结果
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, f"执行超时 (>{timeout}秒)"

    except Exception as e:
        return False, f"执行异常: {str(e)}"

    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except:
            pass
