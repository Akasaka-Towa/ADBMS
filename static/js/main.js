document.addEventListener("DOMContentLoaded", () => {
  const themeToggles = document.querySelectorAll("[data-theme-toggle]");

  const setTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("adbms-theme", theme);

    themeToggles.forEach((toggle) => {
      const label = toggle.querySelector("[data-theme-label]");
      const isDark = theme === "dark";
      toggle.setAttribute("aria-pressed", String(isDark));
      if (label) label.textContent = isDark ? "Dark" : "Light";
    });
  };

  const storedTheme = localStorage.getItem("adbms-theme");
  const initialTheme = storedTheme || document.documentElement.dataset.theme || "light";
  setTheme(initialTheme);

  themeToggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const currentTheme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
      setTheme(currentTheme === "dark" ? "light" : "dark");
    });
  });

  const sidebar = document.querySelector("#sidebar");
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");

  if (sidebar && sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  document.querySelectorAll(".app-toast").forEach((toastNode) => {
    const toast = new bootstrap.Toast(toastNode, { delay: 4200 });
    toast.show();
  });

  document.querySelectorAll("[data-confirm]").forEach((button) => {
    button.addEventListener("click", (event) => {
      if (!window.confirm(button.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });

  document.querySelectorAll("[data-table-search]").forEach((input) => {
    input.addEventListener("input", () => {
      const table = input.closest(".surface")?.querySelector("[data-files-table]");
      if (!table) return;

      const query = input.value.trim().toLowerCase();
      table.querySelectorAll("[data-file-row]").forEach((row) => {
        row.style.display = row.innerText.toLowerCase().includes(query) ? "" : "none";
      });
    });
  });

  document.querySelectorAll("[data-upload-form]").forEach((form) => {
    const fileInput = form.querySelector("[data-file-input]");
    const dropZone = form.querySelector("[data-drop-zone]");
    const fileLabel = form.querySelector("[data-file-label]");
    const filePreview = form.querySelector("[data-file-preview]");
    const selectedName = form.querySelector("[data-selected-name]");
    const selectedSize = form.querySelector("[data-selected-size]");
    const clearFile = form.querySelector("[data-clear-file]");
    const progressWrap = form.querySelector("[data-upload-progress]");
    const progressBar = progressWrap?.querySelector(".progress-bar");
    const progressPercent = form.querySelector("[data-upload-percent]");
    const progressStatus = form.querySelector("[data-upload-status]");

    if (!fileInput || !dropZone) return;

    const formatSize = (bytes) => {
      if (!bytes) return "0 KB";
      const units = ["B", "KB", "MB", "GB"];
      const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
      const value = bytes / Math.pow(1024, index);
      return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
    };

    const updateLabel = () => {
      const file = fileInput.files?.[0];
      if (file && fileLabel) {
        fileLabel.textContent = "File ready to upload";
      }
      if (file && filePreview && selectedName && selectedSize) {
        selectedName.textContent = file.name;
        selectedSize.textContent = `${formatSize(file.size)} selected`;
        filePreview.classList.remove("d-none");
      }
    };

    fileInput.addEventListener("change", updateLabel);

    clearFile?.addEventListener("click", () => {
      fileInput.value = "";
      if (fileLabel) fileLabel.textContent = "Drop your file here";
      filePreview?.classList.add("d-none");
      progressWrap?.classList.add("d-none");
      if (progressBar) progressBar.style.width = "0%";
      if (progressPercent) progressPercent.textContent = "0%";
      if (progressStatus) progressStatus.textContent = "Preparing upload";
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        event.stopPropagation();
        dropZone.classList.add("drag-over");
      });
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        event.stopPropagation();
        dropZone.classList.remove("drag-over");
      });
    });

    dropZone.addEventListener("drop", (event) => {
      const files = event.dataTransfer?.files;
      if (files?.length) {
        fileInput.files = files;
        updateLabel();
      }
    });

    form.addEventListener("submit", (event) => {
      if (!fileInput.files?.length) {
        event.preventDefault();
        fileInput.click();
        return;
      }

      if (!progressWrap || !progressBar || !progressPercent || !progressStatus) return;

      progressWrap.classList.remove("d-none");
      let progress = 8;
      progressBar.style.width = `${progress}%`;
      progressPercent.textContent = `${progress}%`;
      progressStatus.textContent = "Preparing file";

      const timer = window.setInterval(() => {
        progress = Math.min(progress + 9, 96);
        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
        if (progress >= 70) {
          progressStatus.textContent = "Replicating backup";
        } else if (progress >= 35) {
          progressStatus.textContent = "Uploading securely";
        }
        if (progress >= 96) {
          progressStatus.textContent = "Finalizing";
          window.clearInterval(timer);
        }
      }, 120);
    });
  });
});
