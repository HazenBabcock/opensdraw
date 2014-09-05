;;
;; Major mode for openlcad.
;;

(defconst lcad-keywords
      `((,(concat "(\\("
		  (regexp-opt '("def" "mirror" "part" "print" "rotate" "set" "translate"))
		  "\\)\\>"
		  "[ \r\n\t]+")
	 (1 font-lock-function-name-face))
	(,(concat "\\<\\("
		  (regexp-opt '("e" "nil" "pi" "t"))
		  "\\)\\>")
	 (1 font-lock-constant-face))))

(progn
  (add-to-list 'auto-mode-alist '("\\.lcad\\'" . lcad-mode)))
;  (add-to-list 'interpreter-mode-alist '("lcad" . lcad-mode)))

(define-derived-mode lcad-mode prog-mode "lcad"
  (setq font-lock-defaults '(lcad-keywords))
)

(provide 'lcad-mode)

;
; The MIT License
;
; Copyright (c) 2014 Hazen Babcock
;
; Permission is hereby granted, free of charge, to any person obtaining a copy
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
; copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:
;
; The above copyright notice and this permission notice shall be included in
; all copies or substantial portions of the Software.
;
; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
; THE SOFTWARE.
;
