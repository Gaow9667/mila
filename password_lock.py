import hashlib
import os

class PasswordLock:
    def __init__(self):
        self.salt = os.urandom(32) # 生成随机盐值
        self.stored_hash = None
        self.is_locked = True

    def set_password(self, password):
        """设置密码：将密码加盐后哈希存储"""
        # 将盐和密码组合
        salted_password = self.salt + password.encode('utf-8')
        # 使用SHA-256进行哈希
        self.stored_hash = hashlib.sha256(salted_password).hexdigest()
        print("密码已设置。")
        self.lock()

    def verify_password(self, password):
        """验证密码：将输入密码加盐哈希后与存储的哈希值对比"""
        if not self.stored_hash:
            print("错误：尚未设置密码。")
            return False
        
        salted_password = self.salt + password.encode('utf-8')
        input_hash = hashlib.sha256(salted_password).hexdigest()
        
        return input_hash == self.stored_hash

    def unlock(self, password):
        if self.verify_password(password):
            self.is_locked = False
            print("解锁成功！")
            return True
        else:
            print("解锁失败：密码错误。")
            return False

    def lock(self):
        self.is_locked = True
        print("已上锁。")

# 演示使用
if __name__ == "__main__":
    lock = PasswordLock()
    
    # 设置密码
    lock.set_password("my_secret_password")
    
    # 尝试错误密码
    print("\n尝试输入错误密码 '123456':")
    lock.unlock("123456")
    
    # 尝试正确密码
    print("\n尝试输入正确密码 'my_secret_password':")
    lock.unlock("my_secret_password")
