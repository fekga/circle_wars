#version 130

precision highp int;
precision highp float;
uniform float time;
uniform vec2 resolution;
uniform vec2 focus;
uniform float map_radius;
uniform float crack_radius;

#pragma include library.shader

void main()
{
	vec3 light = normalize(vec3(4., 2., -1.));
	
	float radius = max(1e-20,map_radius);
	vec2 fc = gl_FragCoord.xy + focus - resolution/2.0;
	vec2 p = tr(fc);

	vec3 col = 	vec3(0.0);

	vec3 lava = vec3(0.0);
	vec3 ground = vec3(0.5,0.3,0.1);
	float vor = 0.0;
	float len = length(fc) + cos(fbm(p*15.0)*15.0)*15.0;
    float crack = smoothstep(radius-crack_radius,radius,len);

	{
		float val = 1.0 + cos(p.x*p.y + fbm(p*5.0) * 20.0 + time*2.0)/ 2.0;
		lava = vec3(val*1.0, val*0.33, val*0.1);
		lava = mix(lava*0.95,lava,len-radius);
		lava *= exp(-1.8);
	}

	{
		float val = 1.0 + sin(fbm(p * 7.5) * 8.0) / 2.0;
		ground *= exp(-val*0.3);
		vec3 sand = vec3(0.2,0.25,0.0);
		ground = mix(ground,sand,val*0.1);
	}

	{
		vor = voronoi(p*3.5).x*(1.0-crack)*0.75;
		vor = 1.0-vor;
		vor *= smoothstep(0.0,radius,len);
	}

	col = mix(ground,lava,crack);
	col = mix(col,lava,smoothstep(radius-crack_radius,radius,vor*radius));

	gl_FragColor = vec4(col, 1.0);
}
