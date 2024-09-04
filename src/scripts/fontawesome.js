import { library, dom } from '@fortawesome/fontawesome-svg-core';
import { faPen } from '@fortawesome/free-solid-svg-icons';

// 編輯的 icon
library.add(faPen);

// 讓 Font Awesome 知道要在 DOM 中查找 icon
dom.watch();
