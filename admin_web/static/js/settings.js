document.addEventListener('DOMContentLoaded', () => {
    const saveButton = document.getElementById('save-reward-settings-btn');
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            const rewardPerReplies = document.getElementById('reward-per-replies').value;
            const attendanceBaseReward = document.getElementById('attendance-base-reward').value;

            const settings = [
                { key: 'reward_per_replies', value: rewardPerReplies },
                { key: 'attendance_base_reward', value: attendanceBaseReward }
            ];

            fetch('/api/v1/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ settings: settings }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('성공적으로 저장되었습니다.');
                } else {
                    alert('저장 실패: ' + data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('저장 중 오류가 발생했습니다.');
            });
        });
    }
});