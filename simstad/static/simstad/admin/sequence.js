(function () {
	function updateSequenceInlineVisibility() {
		const modeSelect = document.querySelector(
			'select[name="layer_display_mode"]',
		);

		const inlineGroup = document.getElementById("sequence_labels-group");

		if (!modeSelect || !inlineGroup) {
			return;
		}

		const isSequential = modeSelect.value === "sequential";

		inlineGroup.classList.toggle("is-hidden", !isSequential);
	}

	document.addEventListener("DOMContentLoaded", function () {
		updateSequenceInlineVisibility();

		const modeSelect = document.querySelector(
			'select[name="layer_display_mode"]',
		);

		if (modeSelect) {
			modeSelect.addEventListener("change", updateSequenceInlineVisibility);
		}
	});
})();
