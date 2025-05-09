document.addEventListener('DOMContentLoaded', () => {
  const setupVoirPlusButton = (buttonId, subpageClass) => {
    const button = document.getElementById(buttonId);
    if (button) {
      button.addEventListener('click', () => {
        const hiddenSubpages = document.querySelectorAll(`.${subpageClass}.hidden`);
        hiddenSubpages.forEach(subpage => {
          subpage.classList.remove('hidden');
        });
        const firstLink = hiddenSubpages[0].querySelector('a');
        if (firstLink) {
          firstLink.focus();
        }
        button.setAttribute('aria-expanded', 'true');
        button.style.display = 'none';
      });
    }
  };

  setupVoirPlusButton('voir-plus-citizens', 'citizen-subpage');
  setupVoirPlusButton('voir-plus-companies', 'company-subpage');
  setupVoirPlusButton('voir-plus-agents', 'agent-subpage');
  setupVoirPlusButton('voir-plus-expertises', 'expertise-subpage');
  setupVoirPlusButton('voir-plus-documents', 'document-subpage');
  setupVoirPlusButton('voir-plus-financements', 'financement-subpage');
  setupVoirPlusButton('voir-plus-outils', 'outil-subpage');
  setupVoirPlusButton('voir-plus-pilotages', 'pilotage-subpage');
});
