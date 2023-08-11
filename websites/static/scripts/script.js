(function ($) {
  "use strict";

  $(function () {
    var header = $(".start-style");
    $(window).scroll(function () {
      var scroll = $(window).scrollTop();

      if (scroll >= 10) {
        header.removeClass("start-style").addClass("scroll-on");
      } else {
        header.removeClass("scroll-on").addClass("start-style");
      }
    });
  });

  //Animation

  $(document).ready(function () {
    $("body.hero-anime").removeClass("hero-anime");
  });

  //Menu On Hover

  $("body").on("mouseenter mouseleave", ".nav-item", function (e) {
    if ($(window).width() > 750) {
      var _d = $(e.target).closest(".nav-item");
      _d.addClass("show");
      setTimeout(function () {
        _d[_d.is(":hover") ? "addClass" : "removeClass"]("show");
      }, 1);
    }
  });

  //Switch light/dark

  $("#switch").on("click", function () {
    if (!$("body").hasClass("dark")) {
      $("body").addClass("dark");
      $("#switch").addClass("switched");
    } else {
      $("body").removeClass("dark");
      $("#switch").removeClass("switched");
    }
  });
})(jQuery);

// gauge
var res = document.getElementById("hidden").textContent;
console.log(res)(
  function () {
    var Needle,
      arc,
      arcEndRad,
      arcStartRad,
      barWidth,
      chart,
      chartInset,
      degToRad,
      el,
      endPadRad,
      height,
      i,
      margin,
      needle,
      numSections,
      padRad,
      percToDeg,
      percToRad,
      percent,
      radius,
      ref,
      sectionIndx,
      sectionPerc,
      startPadRad,
      svg,
      totalPercent,
      width;

    const values = [0.166, 0.5,0.833, 0.833];
    // 0.166->red
    // 0.5->blue
    // 0.833->green
    if (res == -1) {
      percent = 0;
    } else percent = values[res];

    barWidth = 60;

    numSections = 3;

    // / 2 for HALF circle
    sectionPerc = 1 / numSections / 2;

    padRad = 0.05;

    chartInset = 10;

    // start at 270deg
    totalPercent = 0.75;

    el = d3.select(".chart-gauge");

    margin = {
      top: 20,
      right: 20,
      bottom: 30,
      left: 20,
    };

    width = el[0][0].offsetWidth - margin.left - margin.right;

    height = width;

    radius = Math.min(width, height) / 2;

    percToDeg = function (perc) {
      return perc * 360;
    };

    percToRad = function (perc) {
      return degToRad(percToDeg(perc));
    };

    degToRad = function (deg) {
      return (deg * Math.PI) / 180;
    };

    svg = el
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    chart = svg
      .append("g")
      .attr(
        "transform",
        `translate(${(width + margin.left) / 2}, ${(height + margin.top) / 2})`
      );

    // build gauge bg
    for (
      sectionIndx = i = 1, ref = numSections;
      1 <= ref ? i <= ref : i >= ref;
      sectionIndx = 1 <= ref ? ++i : --i
    ) {
      arcStartRad = percToRad(totalPercent);
      arcEndRad = arcStartRad + percToRad(sectionPerc);
      totalPercent += sectionPerc;
      startPadRad = sectionIndx === 0 ? 0 : padRad / 2;
      endPadRad = sectionIndx === numSections ? 0 : padRad / 2;
      arc = d3.svg
        .arc()
        .outerRadius(radius - chartInset)
        .innerRadius(radius - chartInset - barWidth)
        .startAngle(arcStartRad + startPadRad)
        .endAngle(arcEndRad - endPadRad);
      chart
        .append("path")
        .attr("class", `arc chart-color${sectionIndx}`)
        .attr("d", arc);
    }

    Needle = class Needle {
      constructor(len, radius1) {
        this.len = len;
        this.radius = radius1;
      }

      drawOn(el, perc) {
        el.append("circle")
          .attr("class", "needle-center")
          .attr("cx", 0)
          .attr("cy", 0)
          .attr("r", this.radius);
        return el
          .append("path")
          .attr("class", "needle")
          .attr("d", this.mkCmd(perc));
      }

      animateOn(el, perc) {
        var self;
        self = this;
        return el
          .transition()
          .delay(500)
          .ease("elastic")
          .duration(2000)
          .selectAll(".needle")
          .tween("progress", function () {
            return function (percentOfPercent) {
              var progress;
              progress = percentOfPercent * perc;
              return d3.select(this).attr("d", self.mkCmd(progress));
            };
          });
      }

      mkCmd(perc) {
        var centerX,
          centerY,
          leftX,
          leftY,
          rightX,
          rightY,
          thetaRad,
          topX,
          topY;
        thetaRad = percToRad(perc / 2); // half circle
        centerX = 0;
        centerY = 0;
        topX = centerX - this.len * Math.cos(thetaRad);
        topY = centerY - this.len * Math.sin(thetaRad);
        leftX = centerX - this.radius * Math.cos(thetaRad - Math.PI / 2);
        leftY = centerY - this.radius * Math.sin(thetaRad - Math.PI / 2);
        rightX = centerX - this.radius * Math.cos(thetaRad + Math.PI / 2);
        rightY = centerY - this.radius * Math.sin(thetaRad + Math.PI / 2);
        return `M ${leftX} ${leftY} L ${topX} ${topY} L ${rightX} ${rightY}`;
      }
    };

    needle = new Needle(90, 15);

    needle.drawOn(chart, 0);

    needle.animateOn(chart, percent);
  }.call(this)
);


