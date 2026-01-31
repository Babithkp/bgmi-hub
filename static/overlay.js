async function updateOverlay() {  try {
    const res = await fetch("/state");
    const data = await res.json();
    if (!data) return;

    // Images
    document.getElementById("teamLogoSmall").src = data.teamImage;
    document.getElementById("teamLogo").src = data.teamImage;
    document.getElementById("playerImage").src = data.playerImage;

    // Player name
    const name = document.getElementById("playerName");
    name.innerText = data.teamName;
    name.style.background = data.color || "black";

    if (data.ui_position) {
      const p = data.ui_position;
    
      // Small team logo (container)
      const teamSmallWrap = document.getElementById("teamsmallLogo");
      teamSmallWrap.style.top = p.TeamShortLogoTop + "px";
      teamSmallWrap.style.left = p.TeamShortLogoLeft + "px";
      teamSmallWrap.style.width = p.TeamShortLogoWidth + "px";
      teamSmallWrap.style.height = p.TeamShortLogoHeight + "px";
    
      // Team bar (logo + name)
      const teamBar = document.getElementById("teamBar");
      teamBar.style.top = p.TeamLogoTop + "px";
      teamBar.style.left = p.TeamLogoLeft + "px";
    
      const teamLogo = document.getElementById("teamLogo");
      teamLogo.style.width = p.TeamLogoSize + "px";
      teamLogo.style.height = p.TeamLogoSize + "px";
    
      // Player image
      const playerImg = document.getElementById("playerImage");
      playerImg.style.top = p.PlayerImgTop + "px";
      playerImg.style.left = p.PlayerImgLeft + "px";
      playerImg.style.width = p.PlayerImgSize + "px";
      playerImg.style.height = p.PlayerImgSize + "px";
    }
  } catch (e) {
    console.log("Overlay fetch failed", e);
  }
}

// Smooth polling
setInterval(updateOverlay, 800);
