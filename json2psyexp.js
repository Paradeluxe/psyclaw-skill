/**
 * JSON to PsychoPy XML Converter
 * 将 DeepPsych 项目 JSON 文件转换为 PsychoPy .psyexp XML 格式
 */

/**
 * 收集routine中所有的#[start,end,total_num]格式的随机数表达式
 * @param {Object} routineRect - Routine数据
 * @returns {Array} 随机数表达式数组
 */
function collectRandomPatterns(routineRect) {
    const patterns = [];
    const seen = new Set();
    
    function checkValue(value) {
        if (typeof value === 'string' && value.startsWith('#[') && !seen.has(value)) {
            seen.add(value);
            patterns.push(value);
        }
    }
    
    // 检查 avtpComponents 数组方式
    if (routineRect.avtpComponents && Array.isArray(routineRect.avtpComponents)) {
        routineRect.avtpComponents.forEach(component => {
            if (component && typeof component === 'object') {
                Object.keys(component).forEach(dataKey => {
                    checkValue(component[dataKey]);
                });
            }
        });
    }
    // 检查 avtpData 对象方式
    else if (routineRect.avtpData) {
        Object.keys(routineRect.avtpData).forEach(key => {
            const data = routineRect.avtpData[key];
            if (data && typeof data === 'object') {
                Object.keys(data).forEach(dataKey => {
                    checkValue(data[dataKey]);
                });
            }
        });
    }
    
    return patterns;
}

/**
 * 根据#[start,end,total_num]格式生成随机数的Python代码
 * @param {string} pattern - #[start,end,total_num]格式的字符串
 * @returns {Object} {varName, code} - 变量名和Python代码
 */
function generateRandomCodeFromPattern(pattern) {
    // 解析 #[start,end,total_num] 格式
    const match = pattern.match(/^#\[(\d+),(\d+),(\d+)\]$/);
    if (!match) {
        return { varName: null, code: null };
    }
    
    const start = parseInt(match[1]);
    const end = parseInt(match[2]);
    const totalNum = parseInt(match[3]);
    
    // 生成变量名，例如 _rand_1_100_5
    const varName = `_rand_${start}_${end}_${totalNum}`;
    
    // 生成Python代码
    const code = `${varName} = random.sample(range(${start}, ${end + 1}), ${totalNum})`;
    
    return { varName, code };
}

/**
 * 生成随机数初始化代码组件（Begin Experiment）
 * @param {Array} allPatterns - 所有routine中的随机数表达式
 * @returns {string} XML字符串
 */
function generateRandomInitCodeComponent(allPatterns) {
    if (!allPatterns || allPatterns.length === 0) {
        return '';
    }
    
    // 为每个pattern生成导入和初始化代码
    const initCodes = ['import random'];
    const uniquePatterns = [...new Set(allPatterns)];
    
    uniquePatterns.forEach(pattern => {
        const result = generateRandomCodeFromPattern(pattern);
        if (result.varName) {
            // 预生成随机数序列（使用固定种子保证可重复性）
            initCodes.push(`${result.varName} = random.sample(range(${result.varName.split('_')[1]}, ${result.varName.split('_')[2] + 1}), ${result.varName.split('_')[3]})`);
        }
    });
    
    return `      <CodeComponent name="random_init" plugin="None">
        <Param val="" valType="extendedCode" updates="constant" name="Before Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Before JS Experiment"/>
        <Param val="${initCodes.join('\\n')}" valType="extendedCode" updates="constant" name="Begin Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Routine"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin Routine"/>
        <Param val="Py" valType="str" updates="None" name="Code Type"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each JS Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Routine"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Routine"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="random_init" valType="code" updates="None" name="name"/>
      </CodeComponent>\n`;
}

/**
 * 生成routine级别的随机数获取代码组件（Begin Routine）
 * @param {Array} patterns - 该routine中的随机数表达式
 * @param {number} routineIndex - routine索引
 * @returns {string} XML字符串
 */
function generateRoutineRandomCodeComponent(patterns, routineIndex) {
    if (!patterns || patterns.length === 0) {
        return '';
    }
    
    const routineCodes = [];
    
    patterns.forEach(pattern => {
        const result = generateRandomCodeFromPattern(pattern);
        if (result.varName) {
            // 将随机数序列转换为逗号分隔的字符串
            routineCodes.push(`${result.varName}_str = ', '.join(map(str, ${result.varName}))`);
        }
    });
    
    if (routineCodes.length === 0) {
        return '';
    }
    
    return `      <CodeComponent name="routine_random_${routineIndex}" plugin="None">
        <Param val="" valType="extendedCode" updates="constant" name="Before Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Before JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="Begin JS Routine"/>
        <Param val="${routineCodes.join('\\n')}" valType="extendedCode" updates="constant" name="Begin Routine"/>
        <Param val="Py" valType="str" updates="None" name="Code Type"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="Each JS Frame"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Experiment"/>
        <Param val="" valType="extendedCode" updates="constant" name="End JS Routine"/>
        <Param val="" valType="extendedCode" updates="constant" name="End Routine"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="routine_random_${routineIndex}" valType="code" updates="None" name="name"/>
      </CodeComponent>\n`;
}

/**
 * 将 #[start,end,total_num] 表达式替换为对应的变量名
 * @param {string} value - 包含表达式的值
 * @returns {string} 替换后的值
 */
function replaceRandomPatternsInValue(value) {
    if (typeof value !== 'string') {
        return value;
    }
    
    // 查找所有 #[start,end,total_num] 格式
    const pattern = /#\[(\d+),(\d+),(\d+)\]/g;
    
    return value.replace(pattern, (match, start, end, totalNum) => {
        return `_rand_${start}_${end}_${totalNum}_str`;
    });
}

/**
 * 将 JSON 项目数据转换为 PsychoPy XML（v2.0 格式）
 * @param {Object} projectData - DeepPsych 项目数据（符合 flowchart.schema.json v2.0）
 * @returns {string} XML 字符串
 */
function convertToPsyExpXML(projectData) {
    const { routines, loops } = projectData;
    
    // 收集所有routine中的随机数表达式
    const allRandomPatterns = [];
    routines.forEach(routine => {
        const patterns = collectRandomPatternsFromRoutine(routine);
        patterns.forEach(p => {
            if (!allRandomPatterns.includes(p)) {
                allRandomPatterns.push(p);
            }
        });
    });
    
    // 创建 XML 文档
    let xml = '<?xml version="1.0" ?>\n';
    xml += '<PsychoPy2experiment encoding="utf-8" version="2026.1.1">\n';
    
    // 添加 Settings
    xml += generateSettings();
    
    // 添加全局随机数初始化Code组件（如果存在随机数表达式）
    if (allRandomPatterns.length > 0) {
        xml += '  <Routines>\n';
        xml += '    <Routine name="__init__">\n';
        xml += generateRandomInitCodeComponent(allRandomPatterns);
        xml += '    </Routine>\n';
        xml += '  </Routines>\n';
    }
    
    // 添加 Routines
    xml += '  <Routines>\n';
    for (let i = 0; i < routines.length; i++) {
        xml += generateRoutine(routines[i], i, allRandomPatterns);
    }
    xml += '  </Routines>\n';
    
    // 添加 Flow
    xml += '  <Flow>\n';
    if (allRandomPatterns.length > 0) {
        xml += '    <Routine name="__init__"/>\n';
    }
    xml += generateFlow(routines, loops);
    xml += '  </Flow>\n';
    
    xml += '</PsychoPy2experiment>';
    
    return xml;
}

/**
 * 收集 routine 中的随机数表达式
 * @param {Object} routine - routine 数据
 * @returns {Array} 随机数表达式数组
 */
function collectRandomPatternsFromRoutine(routine) {
    const patterns = [];
    
    if (routine.components && Array.isArray(routine.components)) {
        routine.components.forEach(component => {
            collectRandomPatternsFromComponent(component, patterns);
        });
    }
    
    return patterns;
}

/**
 * 检查并收集随机数表达式
 * @param {any} value - 值
 * @param {Array} patterns - 模式数组
 */
function checkValuePattern(value, patterns) {
    if (typeof value === 'string' && value.startsWith('#[') && !patterns.includes(value)) {
        patterns.push(value);
    }
}

/**
 * 从组件中收集随机数表达式
 * @param {Object} component - 组件数据
 * @param {Array} patterns - 模式数组
 */
function collectRandomPatternsFromComponent(component, patterns) {
    if (!component || typeof component !== 'object') return;
    
    Object.keys(component).forEach(key => {
        checkValuePattern(component[key], patterns);
    });
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
 * @param {Object} routine - routine 数据
 * @param {number} index - routine 索引
 * @param {Array} allRandomPatterns - 所有随机数表达式
 */
function generateRoutine(routine, index, allRandomPatterns) {
    const routineName = routine.name || `Routine_${index + 1}`;
    
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
    
    // 收集当前routine中的随机数表达式
    const routinePatterns = collectRandomPatternsFromRoutine(routine);
    
    // 添加routine级别的随机数处理Code组件（如果存在）
    if (routinePatterns.length > 0) {
        xml += generateRoutineRandomCodeComponent(routinePatterns, index);
    }
    
    // 处理 components 数组
    if (routine.components && Array.isArray(routine.components)) {
        for (const component of routine.components) {
            if (component && component.enabled !== false) {
                if (component.type === 'audio') {
                    xml += generateAudioComponentFromSchema(component, routineName);
                } else if (component.type === 'video') {
                    xml += generateVideoComponentFromSchema(component, routineName);
                } else if (component.type === 'text') {
                    xml += generateTextComponentFromSchema(component, routineName);
                } else if (component.type === 'image') {
                    xml += generateImageComponentFromSchema(component, routineName);
                } else if (component.type === 'keyboard') {
                    xml += generateKeyboardComponentFromSchema(component, routineName);
                }
            }
        }
    }
    
    xml += `    </Routine>\n`;
    return xml;
}

/**
 * 从 schema 格式生成 Audio 组件
 */
function generateAudioComponentFromSchema(component, routineName) {
    const name = component.name || `${routineName}_audio`;
    const soundPath = component.path || '';
    const volume = component.volume !== undefined ? component.volume : 1.0;
    const startTime = ((component.startTime || 0) / 1000).toFixed(1);
    const duration = component.duration && component.duration !== -1 ? (component.duration / 1000).toFixed(1) : '';
    const stopWithRoutine = component.stopWithRoutine !== false ? 'True' : 'False';
    const forceEndRoutine = component.forceEndRoutine === true ? 'True' : 'False';
    const loop = component.loop === true ? 'True' : 'False';
    const hamming = component.hamming !== false ? 'True' : 'False';
    const deviceLabel = component.deviceLabel || '';
    
    return `      <SoundComponent name="${name}" plugin="None">
        <Param val="${deviceLabel}" valType="device" updates="None" name="deviceLabel"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${hamming}" valType="bool" updates="constant" name="hamming"/>
        <Param val="${loop}" valType="bool" updates="constant" name="loop"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="${soundPath}" valType="str" updates="set every repeat" name="sound"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="${stopWithRoutine}" valType="bool" updates="constant" name="stopWithRoutine"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="${volume}" valType="num" updates="constant" name="volume"/>
      </SoundComponent>\n`;
}

/**
 * 从 schema 格式生成 Video 组件
 */
function generateVideoComponentFromSchema(component, routineName) {
    const name = component.name || `${routineName}_video`;
    const videoPath = component.path || '';
    const volume = component.volume !== undefined ? component.volume : 1.0;
    const loop = component.loop === true ? 'True' : 'False';
    const startTime = ((component.startTime || 0) / 1000).toFixed(1);
    const duration = component.duration && component.duration !== -1 ? (component.duration / 1000).toFixed(1) : '';
    const stopWithRoutine = component.stopWithRoutine !== false ? 'True' : 'False';
    const forceEndRoutine = component.forceEndRoutine === true ? 'True' : 'False';
    const pos = component.pos || [0, 0];
    const size = component.size || [null, null];
    const opacity = component.opacity !== undefined ? component.opacity : 1.0;
    const ori = component.ori !== undefined ? component.ori : 0;
    const units = component.units || 'from exp settings';
    const flip = component.flip || 'None';
    const anchor = component.anchor || 'center';
    
    const sizeVal = size[0] !== null && size[1] !== null ? `(${size[0]}, ${size[1]})` : '';
    
    return `      <MovieComponent name="${name}" plugin="None">
        <Param val="${anchor}" valType="str" updates="constant" name="anchor"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${flip}" valType="str" updates="constant" name="flip"/>
        <Param val="${videoPath}" valType="str" updates="set every repeat" name="movie"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="${opacity}" valType="num" updates="constant" name="opacity"/>
        <Param val="(${pos[0]}, ${pos[1]})" valType="list" updates="constant" name="pos"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="${stopWithRoutine}" valType="bool" updates="constant" name="stopWithRoutine"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
        <Param val="${units}" valType="str" updates="None" name="units"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="${volume}" valType="num" updates="constant" name="volume"/>
        <Param val="${loop}" valType="bool" updates="constant" name="loop"/>
      </MovieComponent>\n`;
}

/**
 * 从 schema 格式生成 Text 组件
 */
function generateTextComponentFromSchema(component, routineName) {
    const name = component.name || `${routineName}_text`;
    const text = replaceRandomPatternsInValue(component.text) || '';
    const color = replaceRandomPatternsInValue(component.color) || 'white';
    const font = component.font || 'Arial';
    const letterHeight = component.letterHeight !== undefined ? component.letterHeight : 0.05;
    const pos = component.pos || [0, 0];
    const ori = component.ori !== undefined ? component.ori : 0;
    const opacity = component.opacity !== undefined ? component.opacity : '';
    const startTime = ((component.startTime || 0) / 1000).toFixed(1);
    const duration = component.duration && component.duration !== -1 ? (component.duration / 1000).toFixed(1) : '';
    const units = component.units || 'from exp settings';
    const wrapWidth = component.wrapWidth !== undefined ? component.wrapWidth : '';
    const languageStyle = component.languageStyle || 'LTR';
    const flip = component.flip || 'None';
    const draggable = component.draggable === true ? 'True' : 'False';
    const anchor = component.anchor || 'center';
    const colorSpace = component.colorSpace || 'rgb';
    
    return `      <TextComponent name="${name}" plugin="None">
        <Param val="${anchor}" valType="str" updates="constant" name="anchor"/>
        <Param val="${color}" valType="color" updates="constant" name="color"/>
        <Param val="${colorSpace}" valType="str" updates="constant" name="colorSpace"/>
        <Param val="1" valType="num" updates="constant" name="contrast"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="${draggable}" valType="code" updates="constant" name="draggable"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${flip}" valType="str" updates="constant" name="flip"/>
        <Param val="${font}" valType="str" updates="constant" name="font"/>
        <Param val="${languageStyle}" valType="str" updates="None" name="languageStyle"/>
        <Param val="${letterHeight}" valType="num" updates="constant" name="letterHeight"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="${opacity}" valType="num" updates="constant" name="opacity"/>
        <Param val="${ori}" valType="num" updates="constant" name="ori"/>
        <Param val="(${pos[0]}, ${pos[1]})" valType="list" updates="constant" name="pos"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="True" valType="bool" updates="None" name="syncScreenRefresh"/>
        <Param val="${text}" valType="str" updates="constant" name="text"/>
        <Param val="${units}" valType="str" updates="None" name="units"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="${wrapWidth}" valType="num" updates="constant" name="wrapWidth"/>
      </TextComponent>\n`;
}

/**
 * 从 schema 格式生成 Image 组件
 */
function generateImageComponentFromSchema(component, routineName) {
    const name = component.name || `${routineName}_image`;
    const imagePath = component.path || '';
    const startTime = ((component.startTime || 0) / 1000).toFixed(1);
    const duration = component.duration && component.duration !== -1 ? (component.duration / 1000).toFixed(1) : '';
    const pos = component.pos || [0, 0];
    const size = component.size || [null, null];
    const opacity = component.opacity !== undefined ? component.opacity : 1.0;
    const ori = component.ori !== undefined ? component.ori : 0;
    const contrast = component.contrast !== undefined ? component.contrast : 1.0;
    const color = replaceRandomPatternsInValue(component.color) || '$[1,1,1]';
    const colorSpace = component.colorSpace || 'rgb';
    const flip = component.flip || 'None';
    const interpolate = component.interpolate || 'linear';
    const textureRes = component.textureRes || 128;
    const units = component.units || 'from exp settings';
    const draggable = component.draggable === true ? 'True' : 'False';
    const anchor = 'center';
    
    const flipHoriz = flip === 'Horizontal' || flip === 'Both' ? 'True' : 'False';
    const flipVert = flip === 'Vertical' || flip === 'Both' ? 'True' : 'False';
    
    const sizeVal = size[0] !== null && size[1] !== null ? `(${size[0]}, ${size[1]})` : '';
    
    return `      <ImageComponent name="${name}" plugin="None">
        <Param val="${anchor}" valType="str" updates="constant" name="anchor"/>
        <Param val="${color}" valType="color" updates="constant" name="color"/>
        <Param val="${colorSpace}" valType="str" updates="constant" name="colorSpace"/>
        <Param val="${contrast}" valType="num" updates="constant" name="contrast"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="${draggable}" valType="code" updates="constant" name="draggable"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${flipHoriz}" valType="bool" updates="constant" name="flipHoriz"/>
        <Param val="${flipVert}" valType="bool" updates="constant" name="flipVert"/>
        <Param val="${imagePath}" valType="str" updates="set every repeat" name="image"/>
        <Param val="${interpolate}" valType="str" updates="None" name="interpolate"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="${opacity}" valType="num" updates="constant" name="opacity"/>
        <Param val="${ori}" valType="num" updates="constant" name="ori"/>
        <Param val="(${pos[0]}, ${pos[1]})" valType="list" updates="constant" name="pos"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="True" valType="bool" updates="None" name="syncScreenRefresh"/>
        <Param val="${textureRes}" valType="num" updates="constant" name="texture resolution"/>
        <Param val="${sizeVal}" valType="list" updates="constant" name="size"/>
        <Param val="${units}" valType="str" updates="None" name="units"/>
        <Param val="" valType="code" updates="None" name="validator"/>
      </ImageComponent>\n`;
}

/**
 * 从 schema 格式生成 Keyboard 组件
 */
function generateKeyboardComponentFromSchema(component, routineName) {
    const name = component.name || `${routineName}_key_resp`;
    const startTime = ((component.startTime || 0) / 1000).toFixed(1);
    const duration = component.duration && component.duration !== -1 ? (component.duration / 1000).toFixed(1) : '';
    const stopWithRoutine = component.stopWithRoutine !== false ? 'True' : 'False';
    const forceEndRoutine = component.forceEndRoutine === true ? 'True' : 'False';
    const discardPrevious = component.discardPrevious !== false ? 'True' : 'False';
    const registerOn = component.registerOn || 'press';
    const store = component.store || 'last key';
    const storeCorrect = component.storeCorrect === true ? 'True' : 'False';
    
    // 处理 keys 格式：将 "Space, F, J" 转换为 "'space','f','j'"
    let keys = component.keys || 'f,j';
    if (keys) {
        const keyList = keys.split(',').map(k => k.trim().toLowerCase());
        keys = keyList.map(k => `'${k}'`).join(',');
    } else {
        keys = "'f','j'";
    }
    
    return `      <KeyboardComponent name="${name}" plugin="None">
        <Param val="${keys}" valType="list" updates="constant" name="allowedKeys"/>
        <Param val="" valType="str" updates="constant" name="correctAns"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="${discardPrevious}" valType="bool" updates="constant" name="discard previous"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="${registerOn}" valType="str" updates="constant" name="registerOn"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="${stopWithRoutine}" valType="bool" updates="constant" name="stopWithRoutine"/>
        <Param val="${store}" valType="str" updates="constant" name="store"/>
        <Param val="${storeCorrect}" valType="bool" updates="constant" name="storeCorrect"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
      </KeyboardComponent>\n`;
}

/**
 * 检测 routines 中的变量（以 $ 开头的值）
 */
function detectVariablesFromRoutines(routines, startIndex, endIndex) {
    const variables = new Set();
    const dollarPattern = /\$([^$]+)\$/g;

    for (let i = startIndex; i <= endIndex && i < routines.length; i++) {
        const routine = routines[i];
        if (routine && routine.avtpComponents) {
            routine.avtpComponents.forEach(component => {
                if (component && typeof component === 'object') {
                    Object.values(component).forEach(value => {
                        if (typeof value === 'string') {
                            let match;
                            while ((match = dollarPattern.exec(value)) !== null) {
                                variables.add(match[1]);
                            }
                            dollarPattern.lastIndex = 0;
                        }
                    });
                }
            });
        }
    }
    return Array.from(variables);
}

/**
 * 生成 Flow 部分（支持新旧格式的 loops）
 */
function generateFlow(routines, loops) {
    let xml = '';

    const routineNames = routines.map((rect, index) => rect.name || `Routine_${index + 1}`);

    const processedLoops = loops.map(loop => {
        let startRoutineIndex, endRoutineIndex;
        
        // 新格式：从 list 计算 startPoint 和 endPoint
        // startPoint = first routine's Point - 1, endPoint = last routine's Point + 1
        if (loop.list && Array.isArray(loop.list) && loop.list.length > 0) {
            const routinePoints = loop.list
                .filter(item => item.Point !== undefined)
                .map(item => item.Point)
                .sort((a, b) => a - b);
            
            if (routinePoints.length > 0) {
                const firstPoint = routinePoints[0];
                const lastPoint = routinePoints[routinePoints.length - 1];
                // Point = (routineIndex + 1) * 2, 所以 routineIndex = Point / 2 - 1
                startRoutineIndex = Math.floor(firstPoint / 2) - 1;
                endRoutineIndex = Math.floor(lastPoint / 2) - 1;
            } else {
                // 回退到旧格式
                startRoutineIndex = Math.floor((loop.startPoint - 1) / 2);
                endRoutineIndex = Math.floor((loop.endPoint - 1) / 2);
            }
        } else {
            // 旧格式：直接使用 startPoint 和 endPoint
            startRoutineIndex = Math.floor((loop.startPoint - 1) / 2);
            endRoutineIndex = Math.floor((loop.endPoint - 1) / 2);
        }
        
        const variableNames = detectVariablesFromRoutines(routines, startRoutineIndex, endRoutineIndex);

        return {
            name: loop.name || 'trials',
            reps: loop.nRounds || 1,
            loopType: loop.type || 'sequential',
            conditions: loop.conditions || [],
            startRoutineIndex: startRoutineIndex,
            endRoutineIndex: endRoutineIndex,
            depth: 0,
            variableNames: variableNames
        };
    });
    
    // 根据 loop 的包含关系重新计算深度
    // 被包含越多的 loop，depth 应该越大
    // 使用迭代方式直到 depths 稳定，解决循环依赖问题
    let depthsChanged = true;
    let iterationCount = 0;
    const maxIterations = processedLoops.length + 1;
    
    // 初始化 depth 为 0
    processedLoops.forEach(loop => {
        loop.depth = 0;
    });
    
    while (depthsChanged && iterationCount < maxIterations) {
        depthsChanged = false;
        iterationCount++;
        
        for (let i = 0; i < processedLoops.length; i++) {
            let newDepth = 0;
            for (let j = 0; j < processedLoops.length; j++) {
                if (i === j) continue;
                // 如果 loop j 包含 loop i（j 的范围更大，完全包含 i）
                const jContainsI = processedLoops[j].startRoutineIndex <= processedLoops[i].startRoutineIndex && 
                                   processedLoops[j].endRoutineIndex >= processedLoops[i].endRoutineIndex;
                
                if (jContainsI) {
                    // 检查是否真的是包含（start 更小 或 end 更大）
                    // 或者起点终点都相同但 j 是后加入的（在数组中索引更大）
                    const isStrictlyLarger = (processedLoops[j].startRoutineIndex < processedLoops[i].startRoutineIndex || 
                                              processedLoops[j].endRoutineIndex > processedLoops[i].endRoutineIndex);
                    
                    // 相同起点和终点时，后加入的 loop 包含先加入的
                    const isSameRange = (processedLoops[j].startRoutineIndex === processedLoops[i].startRoutineIndex && 
                                         processedLoops[j].endRoutineIndex === processedLoops[i].endRoutineIndex);
                    
                    if (isStrictlyLarger || (isSameRange && j > i)) {
                        newDepth = Math.max(newDepth, processedLoops[j].depth + 1);
                    }
                }
            }
            
            if (newDepth !== processedLoops[i].depth) {
                processedLoops[i].depth = newDepth;
                depthsChanged = true;
            }
        }
    }
    
    processedLoops.sort((a, b) => a.depth - b.depth);
    
    const activeLoops = new Set();
    
    for (let i = 0; i < routines.length; i++) {
        // 找出在这个 routine 处开始的循环（深度小的先开始）
        const loopsStartingHere = processedLoops.filter(l => 
            l.startRoutineIndex === i && !activeLoops.has(l.name)
        ).sort((a, b) => a.depth - b.depth);
        loopsStartingHere.forEach(loop => {
            xml += generateLoopInitiator(loop);
            activeLoops.add(loop.name);
        });
        
        xml += `    <Routine name="${routineNames[i]}"/>\n`;
        
        // 找出在这个 routine 处结束的循环（深度大的先结束）
        const loopsEndingHere = processedLoops.filter(l => 
            l.endRoutineIndex === i && activeLoops.has(l.name)
        ).sort((a, b) => b.depth - a.depth);
        loopsEndingHere.forEach(loop => {
            xml += generateLoopTerminator(loop);
            activeLoops.delete(loop.name);
        });
    }
    
    return xml;
}

/**
 * 生成 LoopInitiator
 */
function generateLoopInitiator(loop) {
    const conditions = loop.conditions || [];
    const variableNames = loop.variableNames || [];
    let conditionsVal = '';
    let conditionsFileVal = '';

    if (Array.isArray(conditions) && conditions.length > 0) {
        const conditionsArray = conditions.map(condition => {
            const values = condition.values || [];
            const condObj = { name: condition.name || '' };
            variableNames.forEach((varName, index) => {
                condObj[varName] = values[index] !== undefined ? values[index] : '';
            });
            return condObj;
        });
        conditionsVal = JSON.stringify(conditionsArray).replace(/"/g, '&quot;');
    }

    return `    <LoopInitiator loopType="TrialHandler" name="${loop.name}">
      <Param name="Selected rows" updates="None" val="" valType="str"/>
      <Param name="conditions" updates="None" val="${conditionsVal}" valType="str"/>
      <Param name="conditionsFile" updates="None" val="${conditionsFileVal}" valType="file"/>
      <Param name="endPoints" updates="None" val="[0, 1]" valType="code"/>
      <Param name="isTrials" updates="None" val="True" valType="bool"/>
      <Param name="loopType" updates="None" val="${loop.loopType}" valType="str"/>
      <Param name="nReps" updates="None" val="${loop.reps}" valType="code"/>
      <Param name="name" updates="None" val="${loop.name}" valType="code"/>
      <Param name="random seed" updates="None" val="" valType="code"/>
    </LoopInitiator>\n`;
}

/**
 * 生成 LoopTerminator
 */
function generateLoopTerminator(loop) {
    return `    <LoopTerminator name="${loop.name}"/>\n`;
}

// 导出函数（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { convertToPsyExpXML };
}
