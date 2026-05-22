(function () {
  const img = document.getElementById("crop-image");
  const form = document.getElementById("crop-form");
  if (!img || !form) return;

  const src = img.getAttribute("src") || "";
  const isSvg = src.toLowerCase().includes(".svg") || document.querySelector('input[name="logo"]')?.value?.endsWith(".svg");
  if (isSvg || src.endsWith(".svg")) {
    document.getElementById("svg-hint")?.classList.remove("hidden");
    document.querySelector(".crop-container")?.style.setProperty("display", "none");
    return;
  }

  let cropper;
  img.addEventListener("load", function () {
    if (cropper) cropper.destroy();
    cropper = new Cropper(img, {
      aspectRatio: 1,
      viewMode: 1,
      autoCropArea: 0.9,
      responsive: true,
    });
  });
  if (img.complete) img.dispatchEvent(new Event("load"));

  form.addEventListener("submit", function () {
    if (!cropper) return;
    const d = cropper.getData(true);
    document.getElementById("crop_x").value = Math.round(d.x);
    document.getElementById("crop_y").value = Math.round(d.y);
    document.getElementById("crop_w").value = Math.round(d.width);
    document.getElementById("crop_h").value = Math.round(d.height);
  });
})();
