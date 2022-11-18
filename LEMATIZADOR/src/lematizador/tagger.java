package lematizador;

import java.io.Console;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.PrintStream;

import tagger.TestTagger;

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author Erick
 */
public class tagger {
    public tagger(String in, String out)
    {
        try 
        {
            System.setIn( new FileInputStream( new File(in)));		
            System.setOut( new PrintStream(new File(out)));
            System.setErr(new PrintStream(new File("MXPOST_console.txt")));

            TestTagger tagger = new TestTagger();
            //Tem que passar o tagset, aqui eu usei o meu diretório
            String tagset[] = {"MXPOST/port"};
            tagger.main(  tagset );
        } catch (Exception e) {			
                e.printStackTrace();
        }
    }
    
}
