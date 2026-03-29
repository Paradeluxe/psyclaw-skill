/**
 * JSON to PsychoPy XML Converter
 * 将 DeepPsych 项目 JSON 文件转换为 PsychoPy .psyexp XML 格式
 */

/**
 * 将 JSON 项目数据转换为 PsychoPy XML
 * @param {Object} projectData - DeepPsych 项目数据
 * @returns {string} XML 字符串
 */
function convertToPsyExpXML(projectData) {
    const { routineRects, connections } = projectData;
    
    // 创建 XML 文档
    let xml = '<?xml version="1.0" ?>\n';
    xml += '<PsychoPy2experiment encoding="utf-8" version="2026.1.1">\n';
    
    // 添加 Settings
    xml += generateSettings();
    
    // 添加 Routines
    xml += '  <Routines>\n';
    for (const routineRect of routineRects) {
        xml += generateRoutine(routineRect);
    }
    xml += '  </Routines>\n';
    
    // 添加 Flow
    xml += '  <Flow>\n';
    xml += generateFlow(routineRects, connections);
    xml += '  </Flow>\n';
    
    xml += '</PsychoPy2experiment>';
    
    return xml;
}

/**
 * 生成 Settings 部分
 */
function generateSettings() {
    return `  <Settings>
    <Param val="ptb" valType="str" updates="None" name="Audio lib"/>
    <Param val="" valType="str" updates="None" name="Completed URL"/>
    <Param val="auto" valType="str" updates="None" name="Data file delimiter"/>
    <Param val="u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])" valType="code" updates="None" name="Data filename"/>
    <Param val="True" valType="bool" updates="None" name="Enable Escape"/>
    <Param val="Thank you for your participation." valType="str" updates="None" name="End Message"/>
    <Param val="{'participant':'f&quot;{randint(0, 999999):06.0f}&quot;', 'session':'001'}" valType="code" updates="None" name="Experiment info"/>
    <Param val="True" valType="bool" updates="None" name="Force stereo"/>
    <Param val="True" valType="bool" updates="None" name="Full-screen window"/>
    <Param val="" valType="str" updates="None" name="HTML path"/>
    <Param val="" valType="str" updates="None" name="Incomplete URL"/>
    <Param val="testMonitor" valType="str" updates="None" name="Monitor"/>
    <Param val="[]" valType="list" updates="None" name="Resources"/>
    <Param val="False" valType="bool" updates="None" name="Save csv file"/>
    <Param val="False" valType="bool" updates="None" name="Save excel file"/>
    <Param val="False" valType="bool" updates="None" name="Save hdf5 file"/>
    <Param val="True" valType="bool" updates="None" name="Save log file"/>
    <Param val="True" valType="bool" updates="None" name="Save psydat file"/>
    <Param val="True" valType="bool" updates="None" name="Save wide csv file"/>
    <Param val="1" valType="num" updates="None" name="Screen"/>
    <Param val="True" valType="bool" updates="None" name="Show info dlg"/>
    <Param val="False" valType="bool" updates="None" name="Show mouse"/>
    <Param val="height" valType="str" updates="None" name="Units"/>
    <Param val="" valType="str" updates="None" name="Use version"/>
    <Param val="(1024, 768)" valType="list" updates="None" name="Window size (pixels)"/>
    <Param val="none" valType="str" updates="None" name="backgroundFit"/>
    <Param val="" valType="str" updates="None" name="backgroundImg"/>
    <Param val="avg" valType="str" updates="None" name="blendMode"/>
    <Param val="float" valType="str" updates="None" name="clockFormat"/>
    <Param val="{'thisRow.t': 'priority.CRITICAL', 'expName': 'priority.LOW'}" valType="dict" updates="None" name="colPriority"/>
    <Param val="$[0,0,0]" valType="color" updates="None" name="color"/>
    <Param val="rgb" valType="str" updates="None" name="colorSpace"/>
    <Param val="warning" valType="code" updates="None" name="consoleLoggingLevel"/>
    <Param val="default" valType="str" updates="None" name="ecSampleRate"/>
    <Param val="100.1.1.1" valType="str" updates="None" name="elAddress"/>
    <Param val="FILTER_LEVEL_2" valType="str" updates="None" name="elDataFiltering"/>
    <Param val="FILTER_LEVEL_OFF" valType="str" updates="None" name="elLiveFiltering"/>
    <Param val="EYELINK 1000 DESKTOP" valType="str" updates="None" name="elModel"/>
    <Param val="ELLIPSE_FIT" valType="str" updates="None" name="elPupilAlgorithm"/>
    <Param val="PUPIL_AREA" valType="str" updates="None" name="elPupilMeasure"/>
    <Param val="1000" valType="num" updates="None" name="elSampleRate"/>
    <Param val="False" valType="bool" updates="None" name="elSimMode"/>
    <Param val="RIGHT_EYE" valType="str" updates="None" name="elTrackEyes"/>
    <Param val="PUPIL_CR_TRACKING" valType="str" updates="None" name="elTrackingMode"/>
    <Param val="deeppsych_exp" valType="str" updates="None" name="expName"/>
    <Param val="" valType="str" updates="None" name="expVersion"/>
    <Param val="on Sync" valType="str" updates="None" name="exportHTML"/>
    <Param val="None" valType="str" updates="None" name="eyetracker"/>
    <Param val="" valType="code" updates="None" name="frameRate"/>
    <Param val="Attempting to measure frame rate of screen, please wait..." valType="str" updates="None" name="frameRateMsg"/>
    <Param val="127.0.0.1" valType="str" updates="None" name="gpAddress"/>
    <Param val="4242" valType="num" updates="None" name="gpPort"/>
    <Param val="PsychToolbox" valType="str" updates="None" name="keyboardBackend"/>
    <Param val="info" valType="code" updates="None" name="logging level"/>
    <Param val="True" valType="bool" updates="None" name="measureFrameRate"/>
    <Param val="MIDDLE_BUTTON" valType="list" updates="None" name="mgBlink"/>
    <Param val="CONTINUOUS" valType="str" updates="None" name="mgMove"/>
    <Param val="0.5" valType="num" updates="None" name="mgSaccade"/>
    <Param val="neon.local" valType="str" updates="None" name="plCompanionAddress"/>
    <Param val="8080" valType="num" updates="None" name="plCompanionPort"/>
    <Param val="0.6" valType="num" updates="None" name="plConfidenceThreshold"/>
    <Param val="" valType="str" updates="None" name="plPupilCaptureRecordingLocation"/>
    <Param val="127.0.0.1" valType="str" updates="None" name="plPupilRemoteAddress"/>
    <Param val="50020" valType="num" updates="None" name="plPupilRemotePort"/>
    <Param val="1000" valType="num" updates="None" name="plPupilRemoteTimeoutMs"/>
    <Param val="False" valType="bool" updates="None" name="plPupillometryOnly"/>
    <Param val="psychopy_iohub_surface" valType="str" updates="None" name="plSurfaceName"/>
    <Param val="0" valType="code" updates="None" name="runMode"/>
    <Param val="False" valType="bool" updates="None" name="rush"/>
    <Param val="time" valType="str" updates="None" name="sortColumns"/>
    <Param val="" valType="str" updates="None" name="tbLicenseFile"/>
    <Param val="" valType="str" updates="None" name="tbModel"/>
    <Param val="60" valType="num" updates="None" name="tbSampleRate"/>
    <Param val="" valType="str" updates="None" name="tbSerialNo"/>
    <Param val="pyglet" valType="str" updates="None" name="winBackend"/>
  </Settings>
`;
}

/**
 * 生成单个 Routine
 */
function generateRoutine(routineRect) {
    const routineName = routineRect.name || `Routine_${routineRect.id || 'unknown'}`;
    
    let xml = `    <Routine name="${routineName}">\n`;
    
    // 添加 RoutineSettingsComponent
    xml += `      <RoutineSettingsComponent name="${routineName}" plugin="None">
        <Param val="none" valType="str" updates="None" name="backgroundFit"/>
        <Param val="" valType="str" updates="None" name="backgroundImg"/>
        <Param val="$[0,0,0]" valType="color" updates="None" name="color"/>
        <Param val="rgb" valType="str" updates="None" name="colorSpace"/>
        <Param val="" valType="str" updates="constant" name="desc"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="False" valType="code" updates="None" name="forceNonSlip"/>
        <Param val="${routineName}" valType="code" updates="None" name="name"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="constant" name="skipIf"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="" valType="code" updates="constant" name="stopVal"/>
        <Param val="False" valType="bool" updates="None" name="useWindowParams"/>
      </RoutineSettingsComponent>\n`;
    
    // 根据 routine 类型添加组件
    if (routineRect.type === 'Audio') {
        xml += generateAudioComponent(routineRect);
    } else if (routineRect.type === 'Text') {
        xml += generateTextComponent(routineRect);
    } else if (routineRect.type === 'Image') {
        xml += generateImageComponent(routineRect);
    } else if (routineRect.type === 'Keyboard') {
        xml += generateKeyboardComponent(routineRect);
    } else if (routineRect.type === 'Code') {
        xml += generateCodeComponent(routineRect);
    }
    
    xml += `    </Routine>\n`;
    return xml;
}

/**
 * 生成 Audio 组件
 */
function generateAudioComponent(routineRect) {
    const name = routineRect.name || 'sound';
    const soundPath = routineRect.path || '';
    
    return `      <SoundComponent name="${name}" plugin="None">
        <Param val="" valType="device" updates="None" name="deviceLabel"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="False" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="True" valType="bool" updates="constant" name="hamming"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="${soundPath}" valType="str" updates="set every repeat" name="sound"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="0.0" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="" valType="code" updates="constant" name="stopVal"/>
        <Param val="True" valType="bool" updates="constant" name="stopWithRoutine"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="1" valType="num" updates="constant" name="volume"/>
      </SoundComponent>\n`;
}

/**
 * 生成 Text 组件
 */
function generateTextComponent(routineRect) {
    const name = routineRect.name || 'text';
    const text = routineRect.text || '';
    const color = routineRect.color || 'white';
    const pos = routineRect.pos || { x: 0, y: 0 };
    const letterHeight = routineRect.letterHeight || 0.05;
    
    return `      <TextComponent name="${name}" plugin="None">
        <Param val="${color}" valType="color" updates="constant" name="color"/>
        <Param val="rgb" valType="str" updates="constant" name="colorSpace"/>
        <Param val="1" valType="num" updates="constant" name="contrast"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="False" valType="code" updates="constant" name="draggable"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="None" valType="str" updates="constant" name="flip"/>
        <Param val="Arial" valType="str" updates="constant" name="font"/>
        <Param val="LTR" valType="str" updates="None" name="languageStyle"/>
        <Param val="${letterHeight}" valType="num" updates="constant" name="letterHeight"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="" valType="num" updates="constant" name="opacity"/>
        <Param val="0" valType="num" updates="constant" name="ori"/>
        <Param val="(${pos.x}, ${pos.y})" valType="list" updates="constant" name="pos"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="0.0" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="" valType="code" updates="constant" name="stopVal"/>
        <Param val="True" valType="bool" updates="None" name="syncScreenRefresh"/>
        <Param val="${text}" valType="str" updates="constant" name="text"/>
        <Param val="from exp settings" valType="str" updates="None" name="units"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="" valType="num" updates="constant" name="wrapWidth"/>
      </TextComponent>\n`;
}

/**
 * 生成 Image 组件
 */
function generateImageComponent(routineRect) {
    const name = routineRect.name || 'image';
    const imagePath = routineRect.path || '';
    
    return `      <ImageComponent name="${name}" plugin="None">
        <Param val="" valType="device" updates="None" name="deviceLabel"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="False" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="${imagePath}" valType="str" updates="set every repeat" name="image"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="0.0" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="" valType="code" updates="constant" name="stopVal"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
      </ImageComponent>\n`;
}

/**
 * 生成 Keyboard 组件
 */
function generateKeyboardComponent(routineRect) {
    const name = routineRect.name || 'key_resp';
    const allowedKeys = routineRect.allowedKeys || "'f','j'";
    
    return `      <KeyboardComponent name="${name}" plugin="None">
        <Param val="${allowedKeys}" valType="list" updates="constant" name="allowedKeys"/>
        <Param val="" valType="str" updates="constant" name="correctAns"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="True" valType="bool" updates="constant" name="discard previous"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="True" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="press" valType="str" updates="constant" name="registerOn"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="0.0" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="" valType="code" updates="constant" name="stopVal"/>
        <Param val="last key" valType="str" updates="constant" name="store"/>
        <Param val="False" valType="bool" updates="constant" name="storeCorrect"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
      </KeyboardComponent>\n`;
}

/**
 * 生成 Code 组件
 */
function generateCodeComponent(routineRect) {
    const name = routineRect.name || 'code';
    const code = routineRect.code || '';
    
    return `      <CodeComponent name="${name}" plugin="None">
        <Param val="" valType="extendedCode" updates="constant" name="Before Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Before JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Routine"/>
        <Param val="${code}" valType="extendedCode" updates="constant" name="Begin Routine"/>
        <Param val="Py" valType="str" updates="None" name="Code Type"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each JS Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Routine"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Routine"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
      </CodeComponent>\n`;
}

/**
 * 生成 Flow 部分
 */
function generateFlow(routineRects, connections) {
    let xml = '';
    
    // 按照 connections 定义的顺序生成 flow
    // 首先找到所有没有前驱的 routine（起点）
    const routineMap = new Map();
    routineRects.forEach((rect, index) => {
        routineMap.set(rect.id, { ...rect, originalIndex: index });
    });
    
    // 构建连接图
    const graph = new Map();
    const inDegree = new Map();
    
    routineRects.forEach(rect => {
        graph.set(rect.id, []);
        inDegree.set(rect.id, 0);
    });
    
    connections.forEach(conn => {
        const startId = conn.start.routineId;
        const endId = conn.end.routineId;
        
        if (startId && endId && startId !== endId) {
            graph.get(startId).push(endId);
            inDegree.set(endId, inDegree.get(endId) + 1);
        }
    });
    
    // 拓扑排序
    const queue = [];
    const result = [];
    
    routineRects.forEach(rect => {
        if (inDegree.get(rect.id) === 0) {
            queue.push(rect.id);
        }
    });
    
    while (queue.length > 0) {
        const current = queue.shift();
        result.push(current);
        
        const neighbors = graph.get(current) || [];
        neighbors.forEach(neighbor => {
            inDegree.set(neighbor, inDegree.get(neighbor) - 1);
            if (inDegree.get(neighbor) === 0) {
                queue.push(neighbor);
            }
        });
    }
    
    // 如果还有未访问的节点（有环的情况），直接添加
    routineRects.forEach(rect => {
        if (!result.includes(rect.id)) {
            result.push(rect.id);
        }
    });
    
    // 生成 flow XML
    result.forEach(routineId => {
        const routine = routineMap.get(routineId);
        if (routine) {
            xml += `    <Routine name="${routine.name || `Routine_${routineId}`}"/>\n`;
        }
    });
    
    return xml;
}

// 导出函数（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { convertToPsyExpXML };
}
