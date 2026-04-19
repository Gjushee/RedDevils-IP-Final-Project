// Premier League Table — fetched from TheSportsDB API
 
document.addEventListener("DOMContentLoaded", function () {
  const tableBody = document.querySelector("#pl-table tbody");
  if (!tableBody) return;
 
  tableBody.innerHTML = `
    <tr><td colspan="5" class="text-center py-3">Loading table...</td></tr>
  `;
 
  fetch("https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4328&s=2025-2026")
    .then((response) => response.json())
    .then((data) => {
      tableBody.innerHTML = "";
 
      if (!data.table || data.table.length === 0) {
        tableBody.innerHTML = `
          <tr><td colspan="5" class="text-center py-3">Table data not available for this season yet.</td></tr>
        `;
        return;
      }
 
      data.table.forEach((team) => {
        const row = document.createElement("tr");
 
        if (team.strTeam === "Manchester United") {
          row.classList.add("highlight-row");
        }
 
        const played = toNum(team.intPlayed);
        const wins   = toNum(team.intWin);
        const draws  = toNum(team.intDraw);
        const losses = toNum(team.intLoss);
 
        const formHTML = generateLast5Form({ played, wins, draws, losses });
 
        row.innerHTML = `
          <td>${team.intRank ?? "-"}</td>
          <td class="text-start align-middle">
            <img src="${team.strBadge ?? ""}" alt="${team.strTeam ?? "Club"}" class="club-logo me-2">
            ${team.strTeam ?? "Unknown"}
          </td>
          <td>${team.intPlayed ?? "-"}</td>
          <td>${team.intPoints ?? "-"}</td>
          <td class="align-middle">${formHTML}</td>
        `;
 
        tableBody.appendChild(row);
      });
    })
    .catch((error) => {
      console.error("Error fetching PL table:", error);
      tableBody.innerHTML = `
        <tr><td colspan="5" class="text-center py-3 text-danger">Error loading table. Please try again later.</td></tr>
      `;
    });
});
 
function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}
 
function generateLast5Form({ played, wins, draws, losses }) {
  if (!played || played <= 0) {
    return `<span class="text-muted">N/A</span>`;
  }
 
  let wCount = Math.round((wins / played) * 5);
  let dCount = Math.round((draws / played) * 5);
 
  if (wCount + dCount > 5) {
    dCount = Math.max(0, 5 - wCount);
  }
 
  let lCount = 5 - (wCount + dCount);
 
  const arr = [
    ...Array(wCount).fill("W"),
    ...Array(dCount).fill("D"),
    ...Array(lCount).fill("L"),
  ];
 
  shuffle(arr);
 
  return arr.map((r) => {
    if (r === "W") return `<span class="form-circle win">W</span>`;
    if (r === "D") return `<span class="form-circle draw">D</span>`;
    return `<span class="form-circle loss">L</span>`;
  }).join("");
}
 
function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}