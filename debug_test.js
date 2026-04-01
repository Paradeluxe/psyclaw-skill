// 简单的调试测试
console.log('=== Debug Test ===');

// 模拟 routineRect 结构
const routineRect = {
    id: 1,
    name: 'test_routine',
    avtpComponents: []
};

// 测试 createAvtpComponent
function createAvtpComponent(type) {
    const defaults = {
        a: { label: 'Audio', type: 'audio' },
        v: { label: 'Video', type: 'video' },
        t: { label: 'Text', type: 'text' },
        p: { label: 'Picture', type: 'image' },
        k: { label: 'Key', type: 'keyboard' }
    };
    const component = defaults[type] ? JSON.parse(JSON.stringify(defaults[type])) : null;
    if (component) {
        component.id = Date.now() + Math.random().toString(36).substr(2, 9);
        component.enabled = true;
    }
    return component;
}

// 添加组件
console.log('Adding components...');
routineRect.avtpComponents.push(createAvtpComponent('t'));
routineRect.avtpComponents.push(createAvtpComponent('t')); // 重复添加
routineRect.avtpComponents.push(createAvtpComponent('a'));

console.log('Routine components:', routineRect.avtpComponents);
console.log('Component count:', routineRect.avtpComponents.length);

// 测试渲染逻辑
function testRenderComponents(rect) {
    console.log('\n=== Render Test ===');
    if (!rect.avtpComponents || rect.avtpComponents.length === 0) {
        console.log('No components');
        return;
    }
    
    rect.avtpComponents.forEach((component, index) => {
        if (!component || !component.enabled) {
            console.log(`Component ${index}: disabled`);
            return;
        }
        console.log(`Component ${index}: ${component.label} (${component.type}) - ID: ${component.id}`);
    });
}

testRenderComponents(routineRect);

console.log('\n=== Test Complete ===');
