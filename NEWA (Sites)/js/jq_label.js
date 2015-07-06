

      function JQLabel(point, html, classname, pixelOffset) {
        this.point = point;
        this.html = html;
        
        this.classname = classname||"";
        this.pixelOffset = pixelOffset||new GSize(0,0);
        this.hidden = false;
      } 
      
      JQLabel.prototype = new GOverlay();

      JQLabel.prototype.initialize = function(map) {
        var div = $("<div>").css('position','absolute')
          .append($("<div>").addClass(this.classname).html(this.html));
        $(map.getPane(G_MAP_FLOAT_SHADOW_PANE)).append(div);
        this.map_ = map;
        this.div_ = div;
        if (this.hidden) {
          this.hide();
        }
        if (this._events) {
          $.each(this._events, function (i,e) {
            if (i == 'hover') {
              div.hover(e[0],e[1]);
            } else {
              div.bind(i,e);
            }
          });
        }
      }

      JQLabel.prototype.remove = function() {
        this.div_.unbind();
        this.div_.remove();
      }

      JQLabel.prototype.copy = function() {
        return new JQLabel(this.point, this.html, this.classname, this.pixelOffset);
      }

      JQLabel.prototype.redraw = function(force) {
        var p = this.map_.fromLatLngToDivPixel(this.point);
        var h = parseInt(this.div_.height());
        this.div_.css({left:(p.x + this.pixelOffset.width) + "px",
          top:(p.y +this.pixelOffset.height - h) + "px"});
      }

      JQLabel.prototype.show = function() {
        if (this.div_) {
          this.div_.show();
          this.redraw();
        }
        this.hidden = false;
      }
      
      JQLabel.prototype.hide = function() {
        if (this.div_) {
          this.div_.hide();
        }
        this.hidden = true;
      }
      
      JQLabel.prototype.isHidden = function() {
        return this.hidden;
      }
      
      JQLabel.prototype.supportsHide = function() {
        return true;
      }

      JQLabel.prototype.setContents = function(html) {
        this.html = html;
        if (this.div_) {
            this.div_.find("div").html(html);
            this.redraw(true);
        }
      }
      
      JQLabel.prototype.setPoint = function(point) {
        this.point = point;
        this.redraw(true);
      }
      
      JQLabel.prototype.getPoint = function() {
        return this.point;
      }

