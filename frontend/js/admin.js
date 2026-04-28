const API_BASE = 'http://localhost:8000';
let authToken = '';

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    authToken = btoa(`${username}:${password}`);
    
    try {
        const response = await fetch(`${API_BASE}/admin/materials`, {
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            document.getElementById('authForm').style.display = 'none';
            document.getElementById('adminPanel').style.display = 'block';
            loadMaterials();
            loadZones();
            showStatus('✅ Вход выполнен успешно!', 'success');
        } else {
            showStatus('❌ Неверный логин или пароль!', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения к серверу! Убедитесь, что бэкенд запущен.', 'error');
    }
}

async function loadMaterials() {
    const container = document.getElementById('materialsTable');
    container.innerHTML = '<div class="loading">Загрузка...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/admin/materials`, {
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            const materials = await response.json();
            renderMaterialsTable(materials);
        } else {
            container.innerHTML = '<div class="status error">Ошибка загрузки</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="status error">Ошибка подключения</div>';
    }
}

function renderMaterialsTable(materials) {
    const container = document.getElementById('materialsTable');
    
    if (materials.length === 0) {
        container.innerHTML = '<div class="loading">Нет материалов</div>';
        return;
    }
    
    let html = `<table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Цена за тонну</th>
                <th>Цена за мешок</th>
                <th>Ед. изм.</th>
                <th>Тип</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>`;
    
    for (const m of materials) {
        const priceTon = m.price_per_ton ?? '';
        const priceBag = m.price_per_bag ?? '';
        const typeBadge = m.type === 'ton' 
            ? '<span class="badge badge-ton">🪨 Сыпучие материалы</span>' 
            : '<span class="badge badge-bag">🛍️ В мешках</span>';
        
        html += `
        <tr>
            <td><strong>${m.id}</strong></td>
            <td><strong style="color: #2d5a3b;">${escapeHtml(m.name)}</strong></td>
            <td style="min-width: 120px;"><input type="number" id="priceTon_${m.id}" value="${priceTon}" placeholder="—" step="100" class="price-input"></td>
            <td style="min-width: 120px;"><input type="number" id="priceBag_${m.id}" value="${priceBag}" placeholder="—" step="10" class="price-input"></td>
            <td>${escapeHtml(m.unit)}</td>
            <td>${typeBadge}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-edit" onclick="updateMaterial(${m.id})">✏️ Редактировать</button>
                <button class="btn btn-sm btn-delete" onclick="deleteMaterial(${m.id})">🗑️ Удалить</button>
            </td>
        </tr>`;
    }
    
    html += `</tbody></table>`;
    container.innerHTML = html;
}

async function updateMaterial(id) {
    const priceTonInput = document.getElementById(`priceTon_${id}`);
    const priceBagInput = document.getElementById(`priceBag_${id}`);
    const updates = {};
    if (priceTonInput.value) updates.price_per_ton = parseFloat(priceTonInput.value);
    if (priceBagInput.value) updates.price_per_bag = parseFloat(priceBagInput.value);
    
    try {
        const response = await fetch(`${API_BASE}/admin/materials/${id}`, {
            method: 'PUT',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        
        if (response.ok) {
            showStatus('✅ Цена обновлена!', 'success');
            loadMaterials();
        } else {
            showStatus('❌ Ошибка обновления', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function deleteMaterial(id) {
    if (!confirm('Удалить материал?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/materials/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            showStatus('✅ Материал удалён!', 'success');
            loadMaterials();
        } else {
            showStatus('❌ Ошибка удаления', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function createMaterial() {
    const data = {
        key_name: document.getElementById('newKeyName').value,
        name: document.getElementById('newName').value,
        price_per_ton: parseFloat(document.getElementById('newPriceTon').value) || null,
        price_per_bag: parseFloat(document.getElementById('newPriceBag').value) || null,
        unit: document.getElementById('newUnit').value,
        description: document.getElementById('newDesc').value,
        type: document.getElementById('newType').value
    };
    
    if (!data.key_name || !data.name || !data.unit) {
        showStatus('❌ Заполните ключ, название и единицу измерения!', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/materials`, {
            method: 'POST',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showStatus('✅ Материал создан!', 'success');
            loadMaterials();
            document.getElementById('newKeyName').value = '';
            document.getElementById('newName').value = '';
            document.getElementById('newPriceTon').value = '';
            document.getElementById('newPriceBag').value = '';
            document.getElementById('newUnit').value = '';
            document.getElementById('newDesc').value = '';
        } else {
            const error = await response.json();
            showStatus(`❌ Ошибка: ${error.detail}`, 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function loadZones() {
    const container = document.getElementById('zonesTable');
    container.innerHTML = '<div class="loading">Загрузка...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/admin/zones`, {
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            const zones = await response.json();
            renderZonesTable(zones);
        } else {
            container.innerHTML = '<div class="status error">Ошибка загрузки</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="status error">Ошибка подключения</div>';
    }
}

function renderZonesTable(zones) {
    const container = document.getElementById('zonesTable');
    
    if (zones.length === 0) {
        container.innerHTML = '<div class="loading">Нет зон</div>';
        return;
    }
    
    let html = `<table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>🪨 Цена доставки сыпучих (руб)</th>
                <th>💎 Цена доставки мешков (руб)</th>
                <th>Примечание</th>
                <th>Микрорайоны</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>`;
    
    for (const z of zones) {
        const bagPrice = (z.bag_price !== undefined && z.bag_price !== null) ? z.bag_price : 700;
        
        html += `<tr>
            <td><strong>${escapeHtml(String(z.id))}</strong></td>
            <td><strong style="color: #2d5a3b;">${escapeHtml(z.name)}</strong></td>
            <td style="min-width: 130px;"><input type="number" id="zonePrice_${z.id}" value="${z.base_price}" step="500" class="price-input" style="width: 110px;"></td>
            <td style="min-width: 130px;"><input type="number" id="zoneBagPrice_${z.id}" value="${bagPrice}" step="100" class="price-input" style="width: 110px;"></td>
            <td>${escapeHtml(z.note || '-')}</td>
            <td class="microdistricts-cell">
                <div id="microdistrictsList_${z.id}" class="microdistricts-list"><span class="loading-micro">Загрузка...</span></div>
                <div class="add-micro-form" style="margin-top: 10px;">
                    <input type="text" id="microName_${z.id}" placeholder="Название" class="micro-input">
                    <input type="text" id="microSlang_${z.id}" placeholder="Народное название" class="micro-input">
                    <button class="btn btn-sm btn-add" onclick="addMicrodistrictToZone(${z.id})">➕ Добавить</button>
                </div>
            </td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-edit" onclick="updateZone(${z.id})">✏️ Сохранить</button>
                <button class="btn btn-sm btn-delete" onclick="deleteZone(${z.id})">🗑️ Удалить</button>
            </td>
        </tr>`;
    }
    
    html += `</tbody></table>`;
    container.innerHTML = html;
    
    for (const z of zones) {
        loadMicrodistrictsIntoTable(z.id);
    }
}

async function loadMicrodistrictsIntoTable(zoneId) {
    const container = document.getElementById(`microdistrictsList_${zoneId}`);
    if (!container) return;
    
    try {
        const microdistricts = await loadMicrodistricts(zoneId);
        
        if (microdistricts.length === 0) {
            container.innerHTML = '<span class="empty-micro">Нет микрорайонов</span>';
            return;
        }
        
        let html = '';
        for (const md of microdistricts) {
            html += `<div class="microdistrict-item"><span>📍 ${escapeHtml(md.name)}${md.slang_name ? ` (${escapeHtml(md.slang_name)})` : ''}</span><button class="btn-micro-delete" onclick="deleteMicrodistrictFromTable(${md.id}, ${zoneId})">🗑️</button></div>`;
        }
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<span class="empty-micro">Ошибка загрузки</span>';
    }
}

async function deleteMicrodistrictFromTable(microdistrictId, zoneId) {
    if (!confirm('Удалить микрорайон?')) return;
    
    const success = await deleteMicrodistrict(microdistrictId);
    if (success) {
        loadMicrodistrictsIntoTable(zoneId);
        showStatus('✅ Микрорайон удалён!', 'success');
    }
}

async function addMicrodistrictToZone(zoneId) {
    const nameInput = document.getElementById(`microName_${zoneId}`);
    const slangInput = document.getElementById(`microSlang_${zoneId}`);
    const name = nameInput.value.trim();
    const slangName = slangInput.value.trim();
    
    if (!name) {
        showStatus('❌ Введите название микрорайона!', 'error');
        return;
    }
    
    const success = await addMicrodistrict(zoneId, name, slangName);
    if (success) {
        nameInput.value = '';
        slangInput.value = '';
        loadMicrodistrictsIntoTable(zoneId);
        showStatus('✅ Микрорайон добавлен!', 'success');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function updateZone(id) {
    const priceInput = document.getElementById(`zonePrice_${id}`);
    const bagPriceInput = document.getElementById(`zoneBagPrice_${id}`);
    const base_price = parseInt(priceInput.value);
    const bag_price = parseInt(bagPriceInput.value);
    
    try {
        const response = await fetch(`${API_BASE}/admin/zones/${id}`, {
            method: 'PUT',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ base_price, bag_price })
        });
        
        if (response.ok) {
            showStatus('✅ Цены доставки обновлены!', 'success');
            loadZones();
        } else {
            showStatus('❌ Ошибка обновления', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function deleteZone(id) {
    if (!confirm('Удалить зону?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/zones/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            showStatus('✅ Зона удалена!', 'success');
            loadZones();
        } else {
            showStatus('❌ Ошибка удаления', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function createZone() {
    const data = {
        key_name: document.getElementById('newZoneKey').value,
        name: document.getElementById('newZoneName').value,
        base_price: parseInt(document.getElementById('newZonePrice').value),
        bag_price: parseInt(document.getElementById('newZoneBagPrice').value) || 700,
        note: document.getElementById('newZoneNote').value || null
    };
    
    if (!data.key_name || !data.name || !data.base_price) {
        showStatus('❌ Заполните ключ, название и цену!', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/zones`, {
            method: 'POST',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showStatus('✅ Зона создана!', 'success');
            loadZones();
            document.getElementById('newZoneKey').value = '';
            document.getElementById('newZoneName').value = '';
            document.getElementById('newZonePrice').value = '';
            document.getElementById('newZoneBagPrice').value = '';
            document.getElementById('newZoneNote').value = '';
        } else {
            const error = await response.json();
            showStatus(`❌ Ошибка: ${error.detail}`, 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function loadMicrodistricts(zoneId) {
    try {
        const response = await fetch(`${API_BASE}/admin/microdistricts/${zoneId}`, {
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            return await response.json();
        }
        return [];
    } catch (error) {
        console.error('Ошибка загрузки микрорайонов:', error);
        return [];
    }
}

async function addMicrodistrict(zoneId, name, slangName) {
    try {
        const response = await fetch(`${API_BASE}/admin/microdistricts`, {
            method: 'POST',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ zone_id: zoneId, name: name, slang_name: slangName })
        });
        
        if (response.ok) {
            showStatus('✅ Микрорайон добавлен!', 'success');
            return true;
        } else {
            showStatus('❌ Ошибка добавления микрорайона', 'error');
            return false;
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
        return false;
    }
}

async function deleteMicrodistrict(id) {
    try {
        const response = await fetch(`${API_BASE}/admin/microdistricts/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            return true;
        } else {
            showStatus('❌ Ошибка удаления', 'error');
            return false;
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
        return false;
    }
}

async function loadFreeMicrodistricts() {
    const container = document.getElementById('freeMicroTable');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Загрузка...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/admin/free-dolomite-microdistricts`, {
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            const microdistricts = await response.json();
            renderFreeMicroTable(microdistricts);
        } else {
            container.innerHTML = '<div class="status error">Ошибка загрузки</div>';
        }
    } catch (error) {
        container.innerHTML = '<div class="status error">Ошибка подключения</div>';
    }
}

function renderFreeMicroTable(microdistricts) {
    const container = document.getElementById('freeMicroTable');
    
    if (microdistricts.length === 0) {
        container.innerHTML = '<div class="empty-micro">Нет микрорайонов с бесплатной доставкой доломита</div>';
        return;
    }
    
    let html = `<table class="free-micro-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Название микрорайона</th>
                <th>Народное название</th>
                <th>Действия</th>
            </tr>
        </thead>
        <tbody>`;
    
    for (const md of microdistricts) {
        html += `<tr>
            <td>${md.id}</td>
            <td><strong>${escapeHtml(md.name)}</strong></td>
            <td>${escapeHtml(md.slang_name || '-')}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-delete" onclick="deleteFreeMicrodistrict(${md.id})">🗑️ Удалить</button>
            </td>
        </tr>`;
    }
    
    html += `</tbody>
    </table>`;
    container.innerHTML = html;
}

async function addFreeMicrodistrict() {
    const name = document.getElementById('freeMicroName').value.trim();
    const slangName = document.getElementById('freeMicroSlang').value.trim();
    
    if (!name) {
        showStatus('❌ Введите название микрорайона!', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/free-dolomite-microdistricts`, {
            method: 'POST',
            headers: { 'Authorization': `Basic ${authToken}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, slang_name: slangName })
        });
        
        if (response.ok) {
            showStatus('✅ Микрорайон добавлен в список бесплатной доставки доломита!', 'success');
            document.getElementById('freeMicroName').value = '';
            document.getElementById('freeMicroSlang').value = '';
            loadFreeMicrodistricts();
        } else {
            const error = await response.json();
            showStatus(`❌ Ошибка: ${error.detail}`, 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

async function deleteFreeMicrodistrict(id) {
    if (!confirm('Удалить микрорайон из списка бесплатной доставки доломита?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/free-dolomite-microdistricts/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Basic ${authToken}` }
        });
        
        if (response.ok) {
            showStatus('✅ Микрорайон удалён из списка бесплатной доставки доломита!', 'success');
            loadFreeMicrodistricts();
        } else {
            showStatus('❌ Ошибка удаления', 'error');
        }
    } catch (error) {
        showStatus('❌ Ошибка подключения', 'error');
    }
}

function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const btns = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => { tab.classList.remove('active'); });
    btns.forEach(btn => { btn.classList.remove('active'); });
    
    const activeTab = document.getElementById(`${tabName}Tab`);
    if (activeTab) activeTab.classList.add('active');
    
    const activeBtn = Array.from(btns).find(btn => {
        if (tabName === 'materials') return btn.textContent.includes('Материалы');
        if (tabName === 'zones') return btn.textContent.includes('Доставки');
        return false;
    });
    if (activeBtn) activeBtn.classList.add('active');
    
    if (tabName === 'zones') {
        loadFreeMicrodistricts();
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
    setTimeout(() => {
        statusDiv.style.display = 'none';
        statusDiv.className = 'status';
    }, 3000);
}