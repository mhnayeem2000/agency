document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-link]");
    if (!button) {
        return;
    }

    const status = button.parentElement.querySelector(".blog-copy-status");
    try {
        await navigator.clipboard.writeText(button.dataset.copyLink);
        status.textContent = "Link copied";
    } catch {
        status.textContent = "Copy is unavailable in this browser";
    }
});
