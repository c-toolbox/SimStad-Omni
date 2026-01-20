(function () {
    console.log("Script loaded!");

	const LAYER_FIELDSETS = {
		image: [".layer-media", ".layer-image"],
		flow: [".layer-media", ".layer-flow"],
		movie: [".layer-media", ".layer-movie"],
		color: [".layer-color"],
		ndi: [".layer-ndi"],
	};

	const ALL_LAYER_FIELDSETS = Object.values(LAYER_FIELDSETS).flat();

	const CROP_FIELDSETS = {
		slice: [".crop-slice"],
		circle: [".crop-circle"],
	};

	const ALL_CROP_FIELDSETS = Object.values(CROP_FIELDSETS).flat();

	function toggleLayerFieldsets(inline) {
		const typeSelect = inline.querySelector('select[name$="-type"]');
		if (!typeSelect) return;

		const layerType = typeSelect.value;

		// Hide all layer fieldsets
		ALL_LAYER_FIELDSETS.forEach((selector) => {
			inline.querySelectorAll(selector).forEach((fs) => {
				fs.style.display = "none";
			});
		});

		// Show relevant fieldsets
		(LAYER_FIELDSETS[layerType] || []).forEach((selector) => {
			inline.querySelectorAll(selector).forEach((fs) => {
				fs.style.display = "";
			});
		});
	}

	function toggleCropFieldsets(inline) {
		const cropSelect = inline.querySelector('select[name$="-crop_type"]');
		if (!cropSelect) return;

		const cropType = cropSelect.value;

		// Hide all crop fieldsets
		ALL_CROP_FIELDSETS.forEach((selector) => {
			inline.querySelectorAll(selector).forEach((fs) => {
				fs.style.display = "none";
			});
		});

		// Show relevant crop fieldsets
		(CROP_FIELDSETS[cropType] || []).forEach((selector) => {
			inline.querySelectorAll(selector).forEach((fs) => {
				fs.style.display = "";
			});
		});
	}

	function updateInline(inline) {
		toggleLayerFieldsets(inline);
		toggleCropFieldsets(inline);
	}

	function initInline(inline) {
		updateInline(inline);

		const typeSelect = inline.querySelector('select[name$="-type"]');
		if (typeSelect) {
			typeSelect.addEventListener("change", () => updateInline(inline));
		}

		const cropSelect = inline.querySelector('select[name$="-crop_type"]');
		if (cropSelect) {
			cropSelect.addEventListener("change", () => updateInline(inline));
		}
	}

	function init() {
		document.querySelectorAll(".inline-related").forEach(initInline);
	}

	document.addEventListener("formset:added", function (event) {
		initInline(event.target);
	});

	window.addEventListener("load", init);
})();
