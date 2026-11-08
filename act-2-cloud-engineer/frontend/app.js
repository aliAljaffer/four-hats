const form = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const taskList = document.querySelector("#task-list");
const statusMessage = document.querySelector("#status");

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.error || `Request failed (${response.status})`);
  }

  return result;
}

function showStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function renderTasks(tasks) {
  taskList.replaceChildren();

  for (const task of tasks) {
    const item = document.createElement("li");
    const checkbox = document.createElement("input");
    const title = document.createElement("span");

    item.className = task.done ? "task done" : "task";
    checkbox.type = "checkbox";
    checkbox.checked = task.done;
    checkbox.setAttribute("aria-label", `Mark ${task.title} as done`);
    title.textContent = task.title;

    checkbox.addEventListener("change", async () => {
      try {
        await request(`/api/tasks/${task.id}`, {
          method: "PATCH",
          body: JSON.stringify({ done: checkbox.checked }),
        });
        await loadTasks();
      } catch (error) {
        showStatus(error.message, true);
      }
    });

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete";
    deleteButton.textContent = "Delete";
    deleteButton.setAttribute("aria-label", `Delete ${task.title}`);

    deleteButton.addEventListener("click", async () => {
      try {
        await request(`/api/tasks/${task.id}`, { method: "DELETE" });
        await loadTasks();
      } catch (error) {
        showStatus(error.message, true);
      }
    });

    item.append(checkbox, title, deleteButton);
    taskList.append(item);
  }
}

async function loadTasks() {
  try {
    renderTasks(await request("/api/tasks"));
    showStatus("");
  } catch (error) {
    showStatus(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();

  if (!title) {
    showStatus("Enter a task title.", true);
    return;
  }

  try {
    await request("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    titleInput.value = "";
    await loadTasks();
  } catch (error) {
    showStatus(error.message, true);
  }
});

loadTasks();
