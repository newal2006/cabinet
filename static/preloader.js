/**
 * CabiNet — школьная платформа для тестов
 *
 * Автор: Новиков Алексей Валерьевич
 * Год создания: 2026
 * Лицензия: All rights reserved
 *
 * (c) 2026 Новиков Алексей Валерьевич. Все права защищены.
 * Любое копирование, распространение или изменение
 * без письменного разрешения автора запрещено.
 */
/**
 * CabiNet Preloader — мягкая реалистичная анимация
 * Длительность: 5 секунд
 * Слово CABINET остаётся до конца и исчезает вместе со слоганом
 */
(function() {
    const css = `
    /* ==================== ПРЕЛОАДЕР ==================== */
    .cabinet-preloader {
        position: fixed;
        inset: 0;
        background: linear-gradient(135deg, #fafafa 0%, #f0f2f5 50%, #e8ecef 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 99999;
        opacity: 1;
        transition: opacity 1s ease;
        overflow: hidden;
    }

    /* Мягкая подсветка фона */
    .cabinet-preloader::before {
        content: '';
        position: absolute;
        inset: 0;
        background: 
            radial-gradient(circle at 30% 40%, rgba(59,130,246,0.08) 0%, transparent 50%),
            radial-gradient(circle at 70% 60%, rgba(239,68,68,0.06) 0%, transparent 50%);
        animation: bgPulse 6s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes bgPulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }

    /* Всё внутреннее содержимое прячется целиком */
    .cabinet-preloader.hidden {
        opacity: 0;
        pointer-events: none;
    }

    /* Обёртка для слова и слогана — чтобы исчезали вместе */
    .cabinet-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 2;
        position: relative;
    }

    /* ==================== СЛОВО ==================== */
    .cabinet-word {
        display: flex;
        align-items: center;
        gap: 6px;
        position: relative;
        margin-bottom: 50px;
    }

    /* ==================== БУКВЫ ==================== */
    .cabinet-letter {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        font-size: 110px;
        font-weight: 900;
        letter-spacing: -3px;
        opacity: 0;
        display: inline-block;
        position: relative;
        line-height: 1;
        will-change: transform, opacity;
        /* Начальное состояние — буква не видна */
        transform: translate(0, 0) scale(1);
    }

    /* CABI — глубокий тёмно-синий с мягкой тенью */
    .cabinet-letter.cabi {
        color: #1e293b;
        text-shadow: 
            0 2px 4px rgba(30, 41, 59, 0.15),
            0 8px 16px rgba(30, 41, 59, 0.10),
            0 16px 32px rgba(30, 41, 59, 0.08);
    }

    /* NET — тёплый красный с мягким свечением */
    .cabinet-letter.net {
        color: #dc2626;
        text-shadow: 
            0 2px 4px rgba(220, 38, 38, 0.20),
            0 8px 16px rgba(220, 38, 38, 0.15),
            0 16px 32px rgba(220, 38, 38, 0.10),
            0 0 60px rgba(220, 38, 38, 0.25);
    }

    /* Буквы летят только пока прелоадер НЕ имеет класса .word-ready */
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(1) { animation: flySoft1 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 0.2s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(2) { animation: flySoft2 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 0.4s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(3) { animation: flySoft3 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 0.6s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(4) { animation: flySoft4 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 0.8s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(5) { animation: flySoft5 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 1.0s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(6) { animation: flySoft6 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 1.2s; }
    .cabinet-preloader:not(.word-ready) .cabinet-letter:nth-child(7) { animation: flySoft7 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: 1.4s; }

    @keyframes flySoft1 {
        0% { opacity: 0; transform: translate(-250px, -250px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft2 {
        0% { opacity: 0; transform: translate(250px, -250px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft3 {
        0% { opacity: 0; transform: translate(-250px, 250px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft4 {
        0% { opacity: 0; transform: translate(0, 350px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft5 {
        0% { opacity: 0; transform: translate(0, -350px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft6 {
        0% { opacity: 0; transform: translate(350px, 0) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }
    @keyframes flySoft7 {
        0% { opacity: 0; transform: translate(250px, 250px) scale(0.5); filter: blur(8px); }
        60% { opacity: 1; filter: blur(0); }
        100% { opacity: 1; transform: translate(0, 0) scale(1); filter: blur(0); }
    }

    /* Когда прелоадер получил .word-ready — буквы видны и мягко «дышат» */
    .cabinet-preloader.word-ready .cabinet-letter {
        opacity: 1;
        transform: translate(0, 0) scale(1);
        filter: blur(0);
        animation: letterBreathe 3s ease-in-out infinite;
    }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(1) { animation-delay: 0s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(2) { animation-delay: 0.15s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(3) { animation-delay: 0.3s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(4) { animation-delay: 0.45s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(5) { animation-delay: 0.6s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(6) { animation-delay: 0.75s; }
    .cabinet-preloader.word-ready .cabinet-letter:nth-child(7) { animation-delay: 0.9s; }

    @keyframes letterBreathe {
        0%, 100% { transform: translateY(0); filter: brightness(1); }
        50% { transform: translateY(-4px); filter: brightness(1.05); }
    }

    /* ==================== WI-FI ЗНАЧОК ==================== */
    .cabinet-wifi {
        position: absolute;
        top: -45px;
        left: 50%;
        transform: translateX(-50%) scale(0) rotate(-180deg);
        opacity: 0;
        color: #000000;
        transition: all 1s cubic-bezier(0.34, 1.56, 0.64, 1);
        filter: 
            drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))
            drop-shadow(0 4px 12px rgba(16, 185, 129, 0.4));
    }
    .cabinet-wifi.visible {
        transform: translateX(-50%) scale(1) rotate(0);
        opacity: 1;
        animation: wifiLive 2s ease-in-out infinite;
    }
    @keyframes wifiLive {
        0%, 100% {
            filter: 
                drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))
                drop-shadow(0 4px 12px rgba(16, 185, 129, 0.4));
            transform: translateX(-50%) scale(1) rotate(0);
        }
        50% {
            filter: 
                drop-shadow(0 0 20px rgba(16, 185, 129, 0.9))
                drop-shadow(0 6px 20px rgba(16, 185, 129, 0.6));
            transform: translateX(-50%) scale(1.12) rotate(0);
        }
    }

    /* Круговые волны Wi-Fi */
    .cabinet-wifi-waves {
        position: absolute;
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 2px solid #10b981;
        opacity: 0;
        pointer-events: none;
    }
    .cabinet-wifi-waves.active {
        animation: wifiWave 2s ease-out infinite;
    }
    .cabinet-wifi-waves.active:nth-child(2) {
        animation-delay: 0.6s;
    }
    @keyframes wifiWave {
        0% { opacity: 0.8; transform: translateX(-50%) scale(0.5); }
        100% { opacity: 0; transform: translateX(-50%) scale(2.5); }
    }

    /* ==================== СЛОГАН ==================== */
    .cabinet-slogan {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 24px;
        color: #475569;
        font-weight: 500;
        letter-spacing: 1px;
        opacity: 0;
        transform: translateY(30px);
        transition: all 1.2s cubic-bezier(0.22, 1, 0.36, 1);
        text-align: center;
        padding: 0 20px;
        position: relative;
    }
    .cabinet-slogan.visible {
        opacity: 1;
        transform: translateY(0);
    }

    /* Мягкие линии вокруг слогана */
    .cabinet-slogan::before,
    .cabinet-slogan::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 40px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #94a3b8, transparent);
        opacity: 0;
        transition: opacity 1s ease 0.3s;
    }
    .cabinet-slogan::before { left: -20px; }
    .cabinet-slogan::after { right: -20px; }
    .cabinet-slogan.visible::before,
    .cabinet-slogan.visible::after { opacity: 0.6; }

    /* ==================== ПРОГРЕСС-БАР ==================== */
    .cabinet-progress {
        margin-top: 50px;
        width: 260px;
        height: 4px;
        background: rgba(148, 163, 184, 0.15);
        border-radius: 4px;
        overflow: hidden;
        opacity: 0;
        transition: opacity 0.8s ease;
        position: relative;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.06);
    }
    .cabinet-progress.visible { opacity: 1; }
    .cabinet-progress-fill {
        height: 100%;
        width: 0;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 50%, #f59e0b 100%);
        background-size: 200% 100%;
        border-radius: 4px;
        animation: 
            progressFill 3.5s cubic-bezier(0.22, 1, 0.36, 1) forwards,
            progressShine 2s linear infinite;
        animation-delay: 1.5s, 1.5s;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
    }
    @keyframes progressFill {
        0% { width: 0; }
        100% { width: 100%; }
    }
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ==================== МОБИЛЬНАЯ АДАПТАЦИЯ ==================== */
    @media (max-width: 700px) {
        .cabinet-letter { font-size: 72px; letter-spacing: -2px; }
        .cabinet-word { gap: 4px; margin-bottom: 40px; }
        .cabinet-slogan { font-size: 18px; }
        .cabinet-wifi { top: -45px; width: 36px; height: 36px; }
        .cabinet-wifi-waves { top: -45px; width: 48px; height: 48px; }
        .cabinet-progress { width: 200px; }
    }
    @media (max-width: 480px) {
        .cabinet-letter { font-size: 52px; letter-spacing: -1px; }
        .cabinet-word { gap: 3px; margin-bottom: 30px; }
        .cabinet-slogan { font-size: 15px; letter-spacing: 0.5px; }
        .cabinet-wifi { top: -35px; width: 30px; height: 30px; }
        .cabinet-wifi-waves { top: -35px; width: 40px; height: 40px; }
        .cabinet-progress { width: 160px; margin-top: 35px; }
    }
    @media (max-width: 360px) {
        .cabinet-letter { font-size: 42px; }
        .cabinet-slogan { font-size: 13px; }
    }
    `;

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    function createPreloader(options = {}) {
        const slogan = options.slogan || 'УРОК НАЧИНАЕТСЯ ЗДЕСЬ';
        const duration = options.duration || 5000;

        const preloader = document.createElement('div');
        preloader.className = 'cabinet-preloader';
        preloader.id = 'cabinetPreloader';
        preloader.innerHTML = `
            <div class="cabinet-inner">
                <div class="cabinet-word" id="cabinetWord">
                    <span class="cabinet-letter cabi">C</span>
                    <span class="cabinet-letter cabi">A</span>
                    <span class="cabinet-letter cabi">B</span>
                    <span class="cabinet-letter cabi" id="letterI" style="position:relative;">
                        I
                        <svg class="cabinet-wifi" id="wifiIcon" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
                            <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
                            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
                            <circle cx="12" cy="20" r="1" fill="currentColor"/>
                        </svg>
                    </span>
                    <span class="cabinet-letter net">N</span>
                    <span class="cabinet-letter net">E</span>
                    <span class="cabinet-letter net">T</span>
                </div>
                <div class="cabinet-slogan" id="cabinetSlogan">${slogan}</div>
                <div class="cabinet-progress" id="cabinetProgress">
                    <div class="cabinet-progress-fill"></div>
                </div>
            </div>
        `;

        document.body.appendChild(preloader);

        // ============ ТАЙМИНГИ ============
        // 0.2-2.8с: буквы летят
        // 2.8с:    прелоадер получает .word-ready → буквы остаются + «дышат»
        // 3.0с:    Wi-Fi появляется
        // 3.5с:    круговые волны
        // 3.8с:    слоган появляется
        // 5.0с:    весь прелоадер (слово + слоган + прогресс) исчезает ВМЕСТЕ

        // 1. Всё слово на месте → переключаемся на "дышащее" состояние
        setTimeout(() => {
            preloader.classList.add('word-ready');
            const wifi = document.getElementById('wifiIcon');
            if (wifi) {
                wifi.classList.add('visible');
                setTimeout(() => {
                    const parent = wifi.parentElement;
                    for (let i = 0; i < 2; i++) {
                        const wave = document.createElement('div');
                        wave.className = 'cabinet-wifi-waves active';
                        parent.appendChild(wave);
                    }
                }, 500);
            }
        }, 2800);

        // 2. Слоган
        setTimeout(() => {
            document.getElementById('cabinetSlogan')?.classList.add('visible');
        }, 3800);

        // 3. Прогресс-бар
        setTimeout(() => {
            document.getElementById('cabinetProgress')?.classList.add('visible');
        }, 1500);

        // 4. Закрываем ВЕСЬ прелоадер целиком (слово + слоган + прогресс исчезнут вместе)
        setTimeout(() => {
            preloader.classList.add('hidden');
            setTimeout(() => {
                preloader.remove();
                if (typeof options.onComplete === 'function') {
                    options.onComplete();
                }
            }, 1000);
        }, duration);

        return preloader;
    }

    window.CabiNetPreloader = {
        show: createPreloader
    };
})();