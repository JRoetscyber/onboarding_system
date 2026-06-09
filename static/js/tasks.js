document.querySelectorAll(".task-list").forEach((list) => {
  new Sortable(list, {
    group: "tasks",
    animation: 150,
    onAdd: updateColumn,
    onUpdate: updateColumn,
  });
});

function updateColumn(event) {
  const card = event.item;
  const column = card.closest(".kanban-col").dataset.column;
  fetch(`/admin/task/${card.dataset.taskId}/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ column }),
  });
}
