import { library, dom } from "@fortawesome/fontawesome-svg-core"
import { faBookmark as fasBookmark } from "@fortawesome/free-solid-svg-icons"
import { faBookmark as farBookmark } from "@fortawesome/free-regular-svg-icons"

library.add(farBookmark, fasBookmark)
dom.i2svg()