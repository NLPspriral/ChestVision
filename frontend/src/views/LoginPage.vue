<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 顶部悬浮标题栏（毛玻璃效果） -->
      <div class="card-header">
        <div class="header-inner">
          <div class="header-icon">
            <span class="icon-lung">🫁</span>
          </div>
          <div class="header-text">
            <h1 class="system-title">胸片X光智能分析系统</h1>
            <p class="system-desc">基于深度学习的胸部X光影像辅助诊断平台</p>
          </div>
        </div>
      </div>

      <!-- 左侧：登录表单区 -->
      <div class="fixed-area login-area" :class="{ 'slide-out': !isLogin }">
        <div class="form-content">
          <h2 class="form-title">登录</h2>
          <p class="or-text">使用您的账号密码登录</p>
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-width="0"
            size="large"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="rememberMe" class="remember-checkbox"
                  >记住我</el-checkbox
                >
                <el-button
                  link
                  type="primary"
                  class="forgot-link"
                  native-type="button"
                  @click="handleForgotPassword"
                  >忘记密码？</el-button
                >
              </div>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
                round
                >登录</el-button
              >
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧：注册表单区 -->
      <div class="fixed-area register-area" :class="{ 'slide-out': isLogin }">
        <div class="form-content">
          <h2 class="form-title">创建账号</h2>
          <p class="or-text">使用您的邮箱注册</p>
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-width="0"
            size="large"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="name">
              <el-input
                v-model="registerForm.name"
                placeholder="姓名"
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱"
                prefix-icon="Message"
              />
            </el-form-item>
            <el-form-item prop="userType">
              <el-select
                v-model="registerForm.userType"
                placeholder="选择用户类型"
                style="width: 100%"
                :teleported="false"
              >
                <el-option
                  label="👤 病人 — 上传个人胸片、查看报告"
                  value="patient"
                />
                <el-option
                  label="👨‍⚕️ 医生 — 管理病人、编辑病例、分析诊断"
                  value="doctor"
                />
                <el-option
                  label="⚙️ 管理员 — 系统管理、分配医患关系"
                  value="admin"
                />
              </el-select>
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="register-btn"
                :loading="registering"
                @click="handleRegister"
                round
                >注册</el-button
              >
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 滑动遮罩层：默认覆盖右侧注册区，点击后滑到左侧覆盖登录区 -->
      <div class="overlay-panel" :class="{ 'slide-left': !isLogin }">
        <div class="overlay-bg bg-green" :class="{ hidden: !isLogin }"></div>
        <div class="overlay-bg bg-purple" :class="{ hidden: isLogin }"></div>
        <div class="overlay-content">
          <div class="guide-text login-guide" :class="{ hidden: !isLogin }">
            <h2>你好，朋友！</h2>
            <p>注册您的个人信息以使用网站的全部功能</p>
            <el-button class="guide-btn" round @click="toggleLogin"
              >注册</el-button
            >
          </div>
          <div class="guide-text register-guide" :class="{ hidden: isLogin }">
            <h2>欢迎回来！</h2>
            <p>输入您的个人信息以使用网站的全部功能</p>
            <el-button class="guide-btn" round @click="toggleLogin"
              >登录</el-button
            >
          </div>
        </div>
      </div>

      <!-- 忘记密码弹窗 -->
      <el-dialog
        v-model="forgotVisible"
        title="重置密码"
        width="400px"
        :close-on-click-modal="false"
        center
      >
        <el-form
          ref="forgotFormRef"
          :model="forgotForm"
          :rules="forgotRules"
          label-width="0"
          @submit.prevent="handleForgotSubmit"
        >
          <el-form-item prop="username">
            <el-input
              v-model="forgotForm.username"
              placeholder="请输入用户名"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="email">
            <el-input
              v-model="forgotForm.email"
              placeholder="请输入注册邮箱"
              prefix-icon="Message"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="forgotVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="forgotLoading"
            @click="handleForgotSubmit"
            >发送重置链接</el-button
          >
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { forgotPasswordApi, registerApi } from "@/api/auth";
import { useUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const isLogin = ref(true);
const rememberMe = ref(false);

const loginFormRef = ref(null);
const loading = ref(false);
const loginForm = reactive({ username: "", password: "" });
const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 50, message: "用户名长度为 3-50 个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 个字符", trigger: "blur" },
  ],
};

async function handleLogin() {
  const valid = await loginFormRef.value.validate().catch(() => false);
  if (!valid) return;
  loading.value = true;
  try {
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
    });
    ElMessage.success("登录成功");
    router.push(route.query.redirect || "/");
  } catch {
    /* 拦截器已处理 */
  } finally {
    loading.value = false;
  }
}

function toggleLogin() {
  isLogin.value = !isLogin.value;
}

// ── 忘记密码 ──
const forgotVisible = ref(false);
const forgotLoading = ref(false);
const forgotFormRef = ref(null);
const forgotForm = reactive({ username: "", email: "" });
const forgotRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效邮箱", trigger: "blur" },
  ],
};

function handleForgotPassword() {
  forgotForm.username = "";
  forgotForm.email = "";
  forgotVisible.value = true;
}

async function handleForgotSubmit() {
  const valid = await forgotFormRef.value.validate().catch(() => false);
  if (!valid) return;
  forgotLoading.value = true;
  try {
    await forgotPasswordApi({
      username: forgotForm.username,
      email: forgotForm.email,
    });
    ElMessage.success("重置链接已发送，请查收邮件");
    forgotVisible.value = false;
  } catch (err) {
    const msg = err?.response?.data?.detail || "操作失败";
    ElMessage.error(msg);
  } finally {
    forgotLoading.value = false;
  }
}

const registerFormRef = ref(null);
const registering = ref(false);
const registerForm = reactive({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  userType: "patient",
});
const registerRules = {
  name: [
    { required: true, message: "请输入姓名", trigger: "blur" },
    { min: 2, max: 20, message: "姓名长度 2-20 个字符", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" },
  ],
  userType: [{ required: true, message: "请选择用户类型", trigger: "change" }],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少 6 个字符", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    {
      validator: (rule, value, callback) =>
        callback(
          value !== registerForm.password
            ? new Error("两次输入的密码不一致")
            : undefined,
        ),
      trigger: "blur",
    },
  ],
};

async function handleRegister() {
  const valid = await registerFormRef.value.validate().catch(() => false);
  if (!valid) return;
  registering.value = true;
  try {
    await registerApi({
      username: registerForm.name,
      email: registerForm.email,
      password: registerForm.password,
      user_type: registerForm.userType,
    });
    ElMessage.success("注册成功，请登录");
    isLogin.value = true;
  } catch {
    /* 拦截器已处理 */
  } finally {
    registering.value = false;
  }
}
</script>

<style scoped>
/* ========== 颜色变量 ========== */
.login-page {
  --login: #1b9e7e;
  --login-l: #2dcdb0;
  --login-d: #0f594b;
  --login-h: #15876c;
  --login-hl: #25b89b;
  --reg: #6c3cb0;
  --reg-l: #9f6bdb;
  --reg-d: #46247a;
  --reg-h: #5b2f99;
  --reg-hl: #8a58c9;

  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fb;
  padding: 20px;
  box-sizing: border-box;
  z-index: 1000;
}

/* ========== 卡片容器 ========== */
.login-card {
  position: relative;
  width: 1000px;
  max-width: 100%;
  min-height: 680px;
  background: #fff;
  border-radius: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* ========== 顶部毛玻璃标题栏 ========== */
.card-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 90px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  z-index: 15;
  display: flex;
  align-items: center;
  padding: 0 40px;
  box-sizing: border-box;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
.header-inner {
  display: flex;
  align-items: center;
  gap: 18px;
  width: 100%;
}
.header-icon {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, var(--login), var(--login-l));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(27, 158, 126, 0.3);
}
.icon-lung {
  font-size: 28px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}
.header-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.system-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.3px;
  line-height: 1.3;
}
.system-desc {
  font-size: 13px;
  color: #666;
  margin: 4px 0 0;
}

/* ========== 左右表单区 ========== */
.fixed-area {
  position: absolute;
  top: 90px;
  height: calc(100% - 90px);
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px 40px 40px;
  box-sizing: border-box;
  background: #fff;
  z-index: 1;
  overflow: hidden;
}
.login-area {
  left: 0;
}
.register-area {
  left: 50%;
  border-left: 2px solid rgba(224, 229, 236, 0.5);
}

/* 表单内容：向外滑出（不重叠） */
.form-content {
  width: 100%;
  max-width: 340px;
  transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(0);
}
/* 登录区隐藏时 → 向左滑出卡片 */
.login-area.slide-out .form-content {
  transform: translateX(-120%);
}
/* 注册区隐藏时 → 向右滑出卡片 */
.register-area.slide-out .form-content {
  transform: translateX(120%);
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}
.or-text {
  color: #8a8f99;
  font-size: 14px;
  margin-bottom: 28px;
}

/* 记住我 / 忘记密码 */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -4px 0 18px 0;
  height: 32px;
}
.remember-checkbox {
  --el-checkbox-font-size: 13px;
}
.remember-checkbox :deep(.el-checkbox__label) {
  color: #666;
}
.forgot-link {
  font-size: 13px;
  padding: 0;
  height: auto;
  line-height: 32px;
}

/* ========== 输入框焦点样式 ========== */
:deep(.el-input__wrapper) {
  transition: all 0.3s ease;
  border-radius: 8px;
}
.login-area :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--login);
  transform: translateY(-1px);
}
.register-area :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--reg);
  transform: translateY(-1px);
}
.login-area :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--login);
  border-color: var(--login);
}
.login-area :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: var(--login);
}

/* ========== 按钮 ========== */
.login-btn,
.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 40px;
  transition: all 0.25s ease;
}
.login-btn {
  background: linear-gradient(135deg, var(--login), var(--login-l));
  color: #fff;
}
.login-btn:hover {
  transform: scale(0.96);
  background: linear-gradient(135deg, var(--login-h), var(--login-hl));
}
.login-btn:active {
  transform: scale(0.92);
}
.register-btn {
  background: linear-gradient(135deg, var(--reg), var(--reg-l));
  color: #fff;
}
.register-btn:hover {
  transform: scale(0.96);
  background: linear-gradient(135deg, var(--reg-h), var(--reg-hl));
}
.register-btn:active {
  transform: scale(0.92);
}

/* ========== 滑动遮罩层 ========== */
.overlay-panel {
  position: absolute;
  top: 90px;
  width: 50%;
  height: calc(100% - 90px);
  left: 50%;
  z-index: 10;
  transition: left 0.55s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.overlay-panel.slide-left {
  left: 0;
}

.overlay-bg {
  position: absolute;
  inset: 0;
  transition: opacity 0.45s ease;
  will-change: opacity;
}
.bg-green {
  background: linear-gradient(135deg, var(--login-d), var(--login-l));
}
.bg-purple {
  background: linear-gradient(135deg, var(--reg-d), var(--reg-l));
}
.overlay-bg.hidden {
  opacity: 0;
}

.overlay-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guide-text {
  position: absolute;
  text-align: center;
  color: #fff;
  max-width: 260px;
  padding: 20px;
  transition:
    opacity 0.35s ease,
    visibility 0.35s;
  visibility: visible;
  opacity: 1;
}
.guide-text.hidden {
  opacity: 0;
  visibility: hidden;
}
.guide-text h2 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
}
.guide-text p {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 28px;
  line-height: 1.6;
}

.guide-btn {
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.6);
  color: #fff;
  padding: 12px 40px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 40px;
  transition: all 0.3s ease;
}
.guide-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #fff;
  transform: scale(0.96);
}
.guide-btn:active {
  transform: scale(0.92);
}

/* 下拉框浮层修复 */
.el-select-dropdown {
  z-index: 3000 !important;
}
.el-popper.is-pure {
  z-index: 3000 !important;
}

/* ========== 移动端 ========== */
@media (max-width: 768px) {
  .login-card {
    min-height: auto;
    border-radius: 24px;
  }
  .card-header {
    height: 70px;
    padding: 0 20px;
  }
  .header-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
  }
  .icon-lung {
    font-size: 22px;
  }
  .system-title {
    font-size: 18px;
  }
  .system-desc {
    font-size: 11px;
  }
  .fixed-area {
    top: 70px;
    height: calc(100% - 70px);
    position: relative;
    width: 100%;
    height: auto;
    min-height: 320px;
    left: 0 !important;
    border-left: none !important;
    padding: 30px 24px;
  }
  .register-area {
    border-top: 1px solid #eee;
  }
  .overlay-panel {
    display: none;
  }
}
</style>
