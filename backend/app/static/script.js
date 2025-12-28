document.getElementById('generate').addEventListener('click', async () => {
    const topic = document.getElementById('topic').value.trim();
    const status = document.getElementById('status');
    const video = document.getElementById('preview');

    if (!topic) {
        status.textContent = '⚠️ Please enter a topic.';
        return;
    }

    status.textContent = '🎬 Generating... This may take a minute.';
    video.style.display = 'none';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_type: 'family_guy', topic })
        });

        const result = await response.json();

        if (response.ok) {
            status.textContent = '✅ Video ready!';
            video.src = result.video_url;
            video.style.display = 'block';
            video.load();
        } else {
            status.textContent = `❌ Error: ${result.detail || 'Unknown error'}`;
        }
    } catch (err) {
        status.textContent = `❌ Network error: ${err.message}`;
    }
});