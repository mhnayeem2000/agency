document.addEventListener("DOMContentLoaded", () => {
    const contentField = document.querySelector("#id_content");
    if (!contentField || !window.ClassicEditor) {
        return;
    }

    const form = contentField.form;
    let preparingSubmit = false;
    const editorReady = ClassicEditor.create(contentField, {
        toolbar: [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
            "insertTable",
            "undo",
            "redo",
        ],
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (preparingSubmit) {
            return;
        }

        preparingSubmit = true;
        const submitter = event.submitter;
        try {
            const editor = await editorReady;
            editor.updateSourceElement();
            if (submitter?.name) {
                const submitterValue = document.createElement("input");
                submitterValue.type = "hidden";
                submitterValue.name = submitter.name;
                submitterValue.value = submitter.value;
                form.append(submitterValue);
            }
            HTMLFormElement.prototype.submit.call(form);
        } catch (error) {
            console.error("The blog editor could not prepare the article for saving.", error);
            window.alert("The editor could not prepare your article for saving. Your writing is still on this page; reload and try again.");
        } finally {
            preparingSubmit = false;
        }
    });
});
