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
 * 将 JSON 项目数据转换为 PsychoPy XML
 * @param {Object} projectData - DeepPsych 项目数据
 * @returns {string} XML 字符串
 */
function convertToPsyExpXML(projectData) {
    const { routineRects, connections } = projectData;
    
    // 收集所有routine中的随机数表达式
    const allRandomPatterns = [];
    routineRects.forEach(rect => {
        const patterns = collectRandomPatterns(rect);
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
    for (let i = 0; i < routineRects.length; i++) {
        xml += generateRoutine(routineRects[i], i, allRandomPatterns);
    }
    xml += '  </Routines>\n';
    
    // 添加 Flow
    xml += '  <Flow>\n';
    if (allRandomPatterns.length > 0) {
        xml += '    <Routine name="__init__"/>\n';
    }
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
function generateRoutine(routineRect, index, allRandomPatterns) {
    const routineName = routineRect.name || `Routine_${index + 1}`;
    
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
    const routinePatterns = collectRandomPatterns(routineRect);
    
    // 添加routine级别的随机数处理Code组件（如果存在）
    if (routinePatterns.length > 0) {
        xml += generateRoutineRandomCodeComponent(routinePatterns, index);
    }
    
    // 处理 avtpComponents 数组中的组件
    if (routineRect.avtpComponents && Array.isArray(routineRect.avtpComponents)) {
        for (const component of routineRect.avtpComponents) {
            if (component && component.enabled) {
                if (component.type === 'audio') {
                    xml += generateAudioComponentFromAvtp(component, routineName);
                } else if (component.type === 'video') {
                    xml += generateVideoComponentFromAvtp(component, routineName);
                } else if (component.type === 'text') {
                    xml += generateTextComponentFromAvtp(component, routineName);
                } else if (component.type === 'image') {
                    xml += generateImageComponentFromAvtp(component, routineName);
                } else if (component.type === 'keyboard') {
                    xml += generateKeyboardComponentFromAvtp(component, routineName);
                }
            }
        }
    } 
    // 兼容旧的 avtpData 对象方式
    else if (routineRect.avtpData) {
        const avtpData = routineRect.avtpData;
        
        if (avtpData.a && avtpData.a.enabled) {
            xml += generateAudioComponentFromAvtp(avtpData.a, routineName);
        }
        if (avtpData.v && avtpData.v.enabled) {
            xml += generateVideoComponentFromAvtp(avtpData.v, routineName);
        }
        if (avtpData.t && avtpData.t.enabled) {
            xml += generateTextComponentFromAvtp(avtpData.t, routineName);
        }
        if (avtpData.p && avtpData.p.enabled) {
            xml += generateImageComponentFromAvtp(avtpData.p, routineName);
        }
        if (avtpData.k && avtpData.k.enabled) {
            xml += generateKeyboardComponentFromAvtp(avtpData.k, routineName);
        }
    } 
    // 兼容更旧的 type 属性方式
    else if (routineRect.type) {
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
    const text = replaceRandomPatternsInValue(routineRect.text) || '';
    const color = replaceRandomPatternsInValue(routineRect.color) || 'white';
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
 * 从 avtpData 生成 Audio 组件
 */
function generateAudioComponentFromAvtp(avtpData, routineName) {
    const name = avtpData.name || `${routineName}_audio`;
    const soundPath = avtpData.path || '';
    const volume = avtpData.volume || 1.0;
    const startTime = (avtpData.startTime || 0) / 1000;
    const duration = avtpData.duration ? avtpData.duration / 1000 : '';
    const stopWithRoutine = avtpData.stopWithRoutine !== false ? 'True' : 'False';
    const forceEndRoutine = avtpData.forceEndRoutine === true ? 'True' : 'False';
    
    return `      <SoundComponent name="${name}" plugin="None">
        <Param val="" valType="device" updates="None" name="deviceLabel"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="True" valType="bool" updates="constant" name="hamming"/>
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
 * 从 avtpData 生成 Video 组件
 */
function generateVideoComponentFromAvtp(avtpData, routineName) {
    const name = avtpData.name || `${routineName}_video`;
    const videoPath = avtpData.path || '';
    const volume = avtpData.volume || 1.0;
    const loop = avtpData.loop ? 'True' : 'False';
    const startTime = (avtpData.startTime || 0) / 1000;
    const duration = avtpData.duration ? avtpData.duration / 1000 : '';
    const stopWithRoutine = avtpData.stopWithRoutine !== false ? 'True' : 'False';
    const forceEndRoutine = avtpData.forceEndRoutine === true ? 'True' : 'False';
    const pos = avtpData.pos || [0, 0];
    const size = avtpData.size || [null, null];
    const opacity = avtpData.opacity || 1.0;
    const anchor = avtpData.anchor || 'center';
    
    return `      <MovieComponent name="${name}" plugin="None">
        <Param val="${anchor}" valType="str" updates="constant" name="anchor"/>
        <Param val="False" valType="bool" updates="None" name="disabled"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
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
        <Param val="from exp settings" valType="str" updates="None" name="units"/>
        <Param val="" valType="code" updates="None" name="validator"/>
        <Param val="${volume}" valType="num" updates="constant" name="volume"/>
        <Param val="${loop}" valType="bool" updates="constant" name="loop"/>
      </MovieComponent>\n`;
}

/**
 * 从 avtpData 生成 Text 组件
 */
function generateTextComponentFromAvtp(avtpData, routineName) {
    const name = avtpData.name || `${routineName}_text`;
    const text = replaceRandomPatternsInValue(avtpData.text) || '';
    const color = replaceRandomPatternsInValue(avtpData.color) || 'white';
    const font = avtpData.font || 'Arial';
    const letterHeight = avtpData.letterHeight || 0.05;
    const pos = avtpData.pos || [0, 0];
    const ori = avtpData.ori || 0;
    // opacity: 如果未设置或为null，使用空字符串
    const opacity = avtpData.opacity !== undefined && avtpData.opacity !== null ? avtpData.opacity : '';
    const contrast = avtpData.contrast || 1.0;
    // startTime: 使用 0.0 格式
    const startTime = ((avtpData.startTime || 0) / 1000).toFixed(1);
    // duration: 如果为 -1 或未设置，使用空字符串
    const duration = avtpData.duration && avtpData.duration !== -1 ? (avtpData.duration / 1000).toFixed(1) : '';
    const units = avtpData.units || 'from exp settings';
    const wrapWidth = avtpData.wrapWidth || '';
    const languageStyle = avtpData.languageStyle || 'LTR';
    const flip = avtpData.flip || 'None';
    const draggable = avtpData.draggable ? 'True' : 'False';
    
    return `      <TextComponent name="${name}" plugin="None">
        <Param val="${color}" valType="color" updates="constant" name="color"/>
        <Param val="rgb" valType="str" updates="constant" name="colorSpace"/>
        <Param val="${contrast}" valType="num" updates="constant" name="contrast"/>
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
 * 从 avtpData 生成 Image 组件
 */
function generateImageComponentFromAvtp(avtpData, routineName) {
    const name = avtpData.name || `${routineName}_image`;
    const imagePath = avtpData.path || '';
    const startTime = (avtpData.startTime || 0) / 1000;
    const duration = avtpData.duration ? avtpData.duration / 1000 : '';
    const pos = avtpData.pos || [0, 0];
    const size = avtpData.size || [null, null];
    const opacity = avtpData.opacity !== undefined && avtpData.opacity !== null ? avtpData.opacity : 1.0;
    const ori = avtpData.ori || 0;
    const contrast = avtpData.contrast !== undefined && avtpData.contrast !== null ? avtpData.contrast : 1.0;
    const color = replaceRandomPatternsInValue(avtpData.color) || '$[1,1,1]';
    const colorSpace = avtpData.colorSpace || 'rgb';
    const flip = avtpData.flip || 'None';
    const interpolate = avtpData.interpolate || 'linear';
    const textureRes = avtpData.textureRes || 128;
    const units = avtpData.units || 'from exp settings';
    const draggable = avtpData.draggable ? 'True' : 'False';

    const flipHoriz = flip === 'horiz' ? 'True' : 'False';
    const flipVert = flip === 'vert' ? 'True' : 'False';

    const sizeVal = size[0] !== null && size[1] !== null ? `(${size[0]}, ${size[1]})` : '';

    return `      <ImageComponent name="${name}" plugin="None">
        <Param val="center" valType="str" updates="constant" name="anchor"/>
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
 * 从 avtpData 生成 Keyboard 组件
 */
function generateKeyboardComponentFromAvtp(avtpData, routineName) {
    const name = avtpData.name || `${routineName}_key_resp`;
    const startTime = (avtpData.startTime || 0) / 1000;
    const duration = avtpData.duration ? avtpData.duration / 1000 : '';
    const forceEndRoutine = avtpData.forceEndRoutine !== false ? 'True' : 'False';
    
    // 处理 keys 格式：将 "Space, F, J" 转换为 "'space','f','j'"
    let keys = avtpData.keys || 'f,j';
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
        <Param val="True" valType="bool" updates="constant" name="discard previous"/>
        <Param val="" valType="code" updates="None" name="durationEstim"/>
        <Param val="${forceEndRoutine}" valType="bool" updates="constant" name="forceEndRoutine"/>
        <Param val="${name}" valType="code" updates="None" name="name"/>
        <Param val="press" valType="str" updates="constant" name="registerOn"/>
        <Param val="True" valType="bool" updates="None" name="saveStartStop"/>
        <Param val="" valType="code" updates="None" name="startEstim"/>
        <Param val="time (s)" valType="str" updates="None" name="startType"/>
        <Param val="${startTime}" valType="code" updates="None" name="startVal"/>
        <Param val="duration (s)" valType="str" updates="None" name="stopType"/>
        <Param val="${duration}" valType="code" updates="constant" name="stopVal"/>
        <Param val="last key" valType="str" updates="constant" name="store"/>
        <Param val="False" valType="bool" updates="constant" name="storeCorrect"/>
        <Param val="True" valType="bool" updates="constant" name="syncScreenRefresh"/>
      </KeyboardComponent>\n`;
}

/**
 * 生成 Flow 部分
 */
function generateFlow(routineRects, connections) {
    let xml = '';
    
    const routineNames = routineRects.map((rect, index) => rect.name || `Routine_${index + 1}`);
    
    const loopConnections = connections.filter(conn => conn.loopName);
    const loops = [];
    
    loopConnections.forEach(conn => {
        const startLabel = parseInt(conn.start.label);
        const endLabel = parseInt(conn.end.label);
        
        // linePoints label 是奇数 (1,3,5,7...)，对应 routine 索引 (0,1,2,3...)
        // 转换公式：index = (label - 1) / 2
        const startRoutineIndex = Math.floor((startLabel - 1) / 2);
        // endLabel 指向 loop 结束的 point，该 point 对应的 routine 索引需要减 1 才是 loop 实际包含的最后一个 routine
        // 例如：endLabel=7 → index=3，但实际包含的是 routine 2（索引从 0），即 routine 3
        let endRoutineIndex = Math.floor((endLabel - 1) / 2);
        
        // 如果 startLabel != endLabel，说明是范围 loop，endRoutineIndex 需要减 1
        // 如果 startLabel == endLabel，说明是 single-point loop，endRoutineIndex 应该等于 startRoutineIndex
        if (startLabel !== endLabel) {
            endRoutineIndex = endRoutineIndex - 1;
        } else {
            endRoutineIndex = startRoutineIndex;
        }
        
        console.log(`Loop ${conn.loopName}: startLabel=${startLabel}, endLabel=${endLabel}, startRoutineIndex=${startRoutineIndex}, endRoutineIndex=${endRoutineIndex}`);
        
        loops.push({
            name: conn.loopName || 'trials',
            reps: conn.loopReps || 1,
            loopType: conn.loopType || 'sequential',
            conditions: conn.loopConditions || '',
            isTrials: conn.loopIsTrials !== false,
            startRoutineIndex: startRoutineIndex,
            endRoutineIndex: endRoutineIndex,
            depth: conn.depth || 0
        });
    });
    
    // 根据 loop 的包含关系重新计算深度
    // 被包含越多的 loop，depth 应该越大
    for (let i = 0; i < loops.length; i++) {
        let depth = 0;
        for (let j = 0; j < loops.length; j++) {
            if (i === j) continue;
            // 如果 loop j 包含 loop i（j 的范围更大，完全包含 i）
            if (loops[j].startRoutineIndex <= loops[i].startRoutineIndex && 
                loops[j].endRoutineIndex >= loops[i].endRoutineIndex &&
                (loops[j].startRoutineIndex < loops[i].startRoutineIndex || 
                 loops[j].endRoutineIndex > loops[i].endRoutineIndex)) {
                depth++;
            }
        }
        loops[i].depth = depth;
        console.log(`Loop ${loops[i].name} recalculated depth: ${depth}`);
    }
    
    loops.sort((a, b) => a.depth - b.depth);
    
    for (let i = 0; i < routineRects.length; i++) {
        // 按 depth 降序排列，外层 loop（depth 小）先放置
        const loopsStartingHere = loops.filter(l => l.startRoutineIndex === i).sort((a, b) => a.depth - b.depth);
        loopsStartingHere.forEach(loop => {
            xml += generateLoopInitiator(loop);
        });
        
        xml += `    <Routine name="${routineNames[i]}"/>\n`;
        
        // 按 depth 升序排列，内层 loop（depth 大）先结束
        const loopsEndingHere = loops.filter(l => l.endRoutineIndex === i).sort((a, b) => b.depth - a.depth);
        loopsEndingHere.forEach(loop => {
            xml += generateLoopTerminator(loop);
        });
    }
    
    return xml;
}

/**
 * 生成 LoopInitiator
 */
function generateLoopInitiator(loop) {
    const conditionsStr = loop.conditions || '';
    let conditionsVal = '';
    let conditionsFileVal = '';
    
    if (conditionsStr) {
        if (conditionsStr.startsWith('[')) {
            // XML 转义：将双引号转为 &quot;
            conditionsVal = conditionsStr.replace(/"/g, '&quot;');
        } else {
            conditionsFileVal = conditionsStr;
        }
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
