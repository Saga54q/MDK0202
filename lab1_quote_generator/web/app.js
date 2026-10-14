/* Логика интерфейса «Генератор случайных цитат».
   Все запросы к серверу выполняются через fetch и обрабатываются
   в try/catch: при ошибке пользователь видит понятное сообщение,
   а в консоль браузера не попадают необработанные исключения (Uncaught). */

"use strict";

const API = {
  categories: "/api/categories",
  quote: "/api/quote",
  login: "/api/login",
};

// Правило проверки имени совпадает с проверкой на сервере
const NAME_PATTERN = /^[А-Яа-яЁёA-Za-z][А-Яа-яЁёA-Za-z\s-]{1,19}$/;

const state = {
  user: null,
};

const element = (id) => document.getElementById(id);

/* ------------------------------------------------------------ утилиты */

function showMessage(node, text, type) {
  node.textContent = text;
  node.classList.remove("message-error", "message-ok", "message-hint");
  node.classList.add(
    type === "error" ? "message-error" :
    type === "ok" ? "message-ok" : "message-hint"
  );
  if (text) {
    console.info("[UI] " + text);
  }
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  let payload = {};
  try {
    payload = await response.json();
  } catch (error) {
    payload = {};
  }
  return { status: response.status, ok: response.ok, payload };
}

function validateLoginForm(name, password) {
  if (!name) {
    return "Введите имя пользователя";
  }
  if (!NAME_PATTERN.test(name)) {
    return "Имя может содержать только буквы, пробел и дефис (от 2 до 20 символов)";
  }
  if (!password) {
    return "Введите код доступа";
  }
  return null;
}

/* -------------------------------------------------------------- вход */

async function handleLogin(event) {
  event.preventDefault();

  const nameNode = element("username");
  const passwordNode = element("password");
  const messageNode = element("login-message");
  const button = element("login-button");

  const name = nameNode.value.trim();
  const password = passwordNode.value;

  const formError = validateLoginForm(name, password);
  if (formError) {
    showMessage(messageNode, formError, "error");
    return;
  }

  button.disabled = true;
  try {
    const result = await requestJson(API.login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: name, password: password }),
    });

    if (result.status === 200) {
      state.user = result.payload.user;
      showMessage(messageNode, "Вход выполнен: " + state.user, "ok");
      element("category").disabled = false;
      element("quote-button").disabled = false;
      element("quote-text").textContent = "Нажмите «Получить цитату».";
      console.info("[UI] Авторизация успешна, статус ответа: 200");
    } else {
      // 400 — ошибка проверки данных, 401 — неверный код доступа
      showMessage(messageNode, result.payload.error || "Не удалось выполнить вход", "error");
      console.warn("[UI] Вход отклонён, статус ответа: " + result.status);
    }
  } catch (error) {
    showMessage(messageNode, "Сервер недоступен, повторите попытку позже", "error");
    console.warn("[UI] Сетевая ошибка при входе: " + error.message);
  } finally {
    button.disabled = false;
  }
}

/* ------------------------------------------------------------ цитаты */

async function loadCategories() {
  const select = element("category");
  try {
    const result = await requestJson(API.categories);
    if (result.status !== 200) {
      console.warn("[UI] Не удалось загрузить категории, статус: " + result.status);
      return;
    }
    result.payload.categories.forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.appendChild(option);
    });
    console.info("[UI] Загружено категорий: " + result.payload.categories.length);
  } catch (error) {
    console.warn("[UI] Сетевая ошибка при загрузке категорий: " + error.message);
  }
}

async function handleQuote(event) {
  event.preventDefault();

  const messageNode = element("quote-message");
  const button = element("quote-button");
  const category = element("category").value;

  if (!state.user) {
    showMessage(messageNode, "Сначала выполните вход", "error");
    return;
  }

  button.disabled = true;
  try {
    const url = category
      ? API.quote + "?category=" + encodeURIComponent(category)
      : API.quote;
    const result = await requestJson(url);

    if (result.status === 200) {
      element("quote-text").textContent = "«" + result.payload.quote.text + "»";
      element("quote-category").textContent =
        "Категория: " + result.payload.quote.category;
      showMessage(messageNode, "Цитата получена", "ok");
      console.info("[UI] Запрос цитаты выполнен, статус ответа: 200");
    } else {
      showMessage(messageNode, result.payload.error || "Цитата не найдена", "error");
      console.warn("[UI] Запрос цитаты отклонён, статус ответа: " + result.status);
    }
  } catch (error) {
    showMessage(messageNode, "Сервер недоступен, повторите попытку позже", "error");
    console.warn("[UI] Сетевая ошибка при запросе цитаты: " + error.message);
  } finally {
    button.disabled = false;
  }
}

/* ------------------------------------------------------------- запуск */

document.addEventListener("DOMContentLoaded", () => {
  element("login-form").addEventListener("submit", handleLogin);
  element("quote-form").addEventListener("submit", handleQuote);
  loadCategories();
  console.info("[UI] Интерфейс загружен, скрипт app.js выполнен");
});
